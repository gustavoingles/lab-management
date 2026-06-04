from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from inventory.choices import TipoMovimentacao
from inventory.models import Estoque, Item, Lote, Movimentacao
from inventory.services.auditoria import registrar_auditoria


def _get_or_create_estoque(item: Item, localizacao_id: int) -> Estoque:
    estoque, _ = Estoque.objects.get_or_create(
        item=item,
        localizacao_id=localizacao_id,
        defaults={
            "quantidade_disponivel": Decimal("0"),
            "quantidade_reservada": Decimal("0"),
        },
    )
    return estoque


@transaction.atomic
def registrar_movimentacao(
    *,
    request,
    item: Item,
    tipo_movimentacao: str,
    quantidade: Decimal,
    localizacao_origem_id: int | None = None,
    localizacao_destino_id: int | None = None,
    lote: Lote | None = None,
    motivo: str = "",
    observacao: str = "",
    requisicao_item=None,
    ordem_servico=None,
    inventario_item=None,
    baixa=None,
    estoque_ja_baixado: bool = False,
    saldo_resultante: Decimal | None = None,
) -> Movimentacao:
    if quantidade <= 0:
        raise ValidationError("Quantidade deve ser maior que zero.")

    saldo_resultante = None

    if tipo_movimentacao == TipoMovimentacao.ENTRADA:
        if not localizacao_destino_id:
            raise ValidationError("Entrada exige localização de destino.")
        estoque = _get_or_create_estoque(item, localizacao_destino_id)
        estoque.quantidade_disponivel += quantidade
        estoque.save(update_fields=["quantidade_disponivel", "atualizado_em"])
        saldo_resultante = estoque.quantidade_disponivel
        if lote:
            lote.quantidade_disponivel += quantidade
            lote.save(update_fields=["quantidade_disponivel", "updated_at"])

    elif tipo_movimentacao == TipoMovimentacao.SAIDA:
        if not localizacao_origem_id:
            raise ValidationError("Saída exige localização de origem.")
        estoque = _get_or_create_estoque(item, localizacao_origem_id)
        if estoque_ja_baixado:
            if saldo_resultante is None:
                estoque.refresh_from_db()
                saldo_resultante = estoque.quantidade_disponivel
        else:
            livre = estoque.quantidade_disponivel - estoque.quantidade_reservada
            if livre < quantidade:
                raise ValidationError(
                    "Saldo livre insuficiente para saída "
                    f"(livre: {livre}, solicitado: {quantidade})."
                )
            if estoque.quantidade_disponivel < quantidade:
                raise ValidationError("Saldo insuficiente para saída.")
            estoque.quantidade_disponivel -= quantidade
            estoque.save(update_fields=["quantidade_disponivel", "atualizado_em"])
            saldo_resultante = estoque.quantidade_disponivel
        if lote:
            if lote.quantidade_disponivel < quantidade:
                raise ValidationError("Saldo do lote insuficiente.")
            lote.quantidade_disponivel -= quantidade
            lote.save(update_fields=["quantidade_disponivel", "updated_at"])

    elif tipo_movimentacao == TipoMovimentacao.TRANSFERENCIA:
        if not localizacao_origem_id or not localizacao_destino_id:
            raise ValidationError("Transferência exige origem e destino.")
        origem = _get_or_create_estoque(item, localizacao_origem_id)
        if origem.quantidade_disponivel < quantidade:
            raise ValidationError("Saldo insuficiente na origem.")
        destino = _get_or_create_estoque(item, localizacao_destino_id)
        origem.quantidade_disponivel -= quantidade
        destino.quantidade_disponivel += quantidade
        origem.save(update_fields=["quantidade_disponivel", "atualizado_em"])
        destino.save(update_fields=["quantidade_disponivel", "atualizado_em"])
        saldo_resultante = destino.quantidade_disponivel

    elif tipo_movimentacao == TipoMovimentacao.AJUSTE:
        if not localizacao_destino_id:
            raise ValidationError("Ajuste exige localização.")
        estoque = _get_or_create_estoque(item, localizacao_destino_id)
        estoque.quantidade_disponivel = quantidade
        estoque.save(update_fields=["quantidade_disponivel", "atualizado_em"])
        saldo_resultante = estoque.quantidade_disponivel

    else:
        raise ValidationError(f"Tipo de movimentação não suportado: {tipo_movimentacao}")

    mov = Movimentacao.objects.create(
        item=item,
        lote=lote,
        usuario=request.user if request else None,
        requisicao_item=requisicao_item,
        ordem_servico=ordem_servico,
        inventario_item=inventario_item,
        baixa=baixa,
        localizacao_origem_id=localizacao_origem_id,
        localizacao_destino_id=localizacao_destino_id,
        tipo_movimentacao=tipo_movimentacao,
        quantidade=quantidade,
        saldo_resultante=saldo_resultante,
        motivo=motivo,
        observacao=observacao,
    )

    registrar_auditoria(
        request=request,
        acao=f"movimentacao.{tipo_movimentacao}",
        entidade="movimentacao",
        entidade_id=mov.id,
        detalhes={"item_id": item.id, "quantidade": str(quantidade)},
    )
    return mov
