from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

from inventory.models import Estoque, Item, Localizacao, Requisicao, RequisicaoItem


def saldo_livre(estoque: Estoque) -> Decimal:
    return estoque.quantidade_disponivel - estoque.quantidade_reservada


def escolher_localizacao_reserva(item: Item, quantidade: Decimal) -> int:
    """Escolhe a localização com maior saldo livre que atenda a quantidade."""
    estoques = (
        Estoque.objects.filter(item=item)
        .select_related("localizacao")
        .filter(localizacao__ativa=True)
    )
    melhor = None
    melhor_livre = Decimal("0")
    for estoque in estoques:
        livre = saldo_livre(estoque)
        if livre >= quantidade and livre > melhor_livre:
            melhor = estoque
            melhor_livre = livre
    if not melhor:
        raise ValidationError(
            f"Saldo livre insuficiente para reservar {quantidade} de {item.nome}. "
            "Verifique entradas de estoque ou outras reservas pendentes."
        )
    return melhor.localizacao_id


@transaction.atomic
def reservar_estoque(*, item_id: int, localizacao_id: int, quantidade: Decimal) -> Estoque:
    if quantidade <= 0:
        raise ValidationError("Quantidade de reserva inválida.")
    estoque = (
        Estoque.objects.select_for_update()
        .filter(item_id=item_id, localizacao_id=localizacao_id)
        .first()
    )
    if not estoque:
        raise ValidationError("Não há estoque nesta localização para o item.")
    if saldo_livre(estoque) < quantidade:
        raise ValidationError(
            f"Saldo livre insuficiente em {estoque.localizacao.nome} "
            f"(livre: {saldo_livre(estoque)}, necessário: {quantidade})."
        )
    estoque.quantidade_reservada = F("quantidade_reservada") + quantidade
    estoque.save(update_fields=["quantidade_reservada", "atualizado_em"])
    estoque.refresh_from_db()
    return estoque


@transaction.atomic
def liberar_reserva_estoque(
    *, item_id: int, localizacao_id: int, quantidade: Decimal
) -> None:
    if quantidade <= 0:
        return
    estoque = (
        Estoque.objects.select_for_update()
        .filter(item_id=item_id, localizacao_id=localizacao_id)
        .first()
    )
    if not estoque:
        return
    if estoque.quantidade_reservada < quantidade:
        raise ValidationError("Reserva de estoque inconsistente ao liberar.")
    estoque.quantidade_reservada = F("quantidade_reservada") - quantidade
    estoque.save(update_fields=["quantidade_reservada", "atualizado_em"])


@transaction.atomic
def reservar_linha_requisicao(linha: RequisicaoItem) -> RequisicaoItem:
    qtd = linha.quantidade_aprovada or linha.quantidade_solicitada
    if linha.localizacao_reserva_id:
        liberar_reserva_linha(linha)
    loc_id = escolher_localizacao_reserva(linha.item, Decimal(qtd))
    reservar_estoque(item_id=linha.item_id, localizacao_id=loc_id, quantidade=Decimal(qtd))
    linha.localizacao_reserva_id = loc_id
    linha.save(update_fields=["localizacao_reserva"])
    return linha


@transaction.atomic
def liberar_reserva_linha(linha: RequisicaoItem) -> None:
    if not linha.localizacao_reserva_id:
        return
    qtd = linha.quantidade_aprovada or linha.quantidade_solicitada
    liberar_reserva_estoque(
        item_id=linha.item_id,
        localizacao_id=linha.localizacao_reserva_id,
        quantidade=Decimal(qtd),
    )
    linha.localizacao_reserva = None
    linha.save(update_fields=["localizacao_reserva"])


@transaction.atomic
def reservar_itens_requisicao(requisicao: Requisicao) -> None:
    if not requisicao.itens.exists():
        raise ValidationError("A requisição não possui itens para reservar.")
    for linha in requisicao.itens.select_related("item"):
        reservar_linha_requisicao(linha)


@transaction.atomic
def liberar_reservas_requisicao(requisicao: Requisicao) -> None:
    for linha in requisicao.itens.all():
        liberar_reserva_linha(linha)


@transaction.atomic
def consumir_reserva_estoque(
    *, item_id: int, localizacao_id: int, quantidade: Decimal
) -> Estoque:
    """Baixa física + remove a reserva (atendimento de requisição)."""
    if quantidade <= 0:
        raise ValidationError("Quantidade inválida.")
    estoque = (
        Estoque.objects.select_for_update()
        .filter(item_id=item_id, localizacao_id=localizacao_id)
        .first()
    )
    if not estoque:
        raise ValidationError("Estoque não encontrado.")
    if estoque.quantidade_reservada < quantidade:
        raise ValidationError("Reserva insuficiente para consumir.")
    if estoque.quantidade_disponivel < quantidade:
        raise ValidationError("Saldo disponível insuficiente.")
    estoque.quantidade_reservada = F("quantidade_reservada") - quantidade
    estoque.quantidade_disponivel = F("quantidade_disponivel") - quantidade
    estoque.save(
        update_fields=["quantidade_reservada", "quantidade_disponivel", "atualizado_em"]
    )
    estoque.refresh_from_db()
    return estoque
