from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from inventory.choices import StatusRequisicao, TipoMovimentacao
from inventory.models import Requisicao, RequisicaoItem
from inventory.services.auditoria import registrar_auditoria
from inventory.services.estoque import registrar_movimentacao


@transaction.atomic
def aprovar_requisicao(*, request, requisicao: Requisicao) -> Requisicao:
    if requisicao.status not in (
        StatusRequisicao.ABERTA,
        StatusRequisicao.EM_APROVACAO,
    ):
        raise ValidationError("Requisição não está pendente de aprovação.")
    requisicao.status = StatusRequisicao.APROVADA
    requisicao.aprovador = request.user
    requisicao.data_aprovacao = timezone.now()
    for linha in requisicao.itens.all():
        if linha.quantidade_aprovada is None:
            linha.quantidade_aprovada = linha.quantidade_solicitada
            linha.save(update_fields=["quantidade_aprovada"])
    requisicao.save(update_fields=["status", "aprovador", "data_aprovacao"])
    registrar_auditoria(
        request=request,
        acao="requisicao.aprovar",
        entidade="requisicao",
        entidade_id=requisicao.id,
    )
    return requisicao


@transaction.atomic
def rejeitar_requisicao(*, request, requisicao: Requisicao, motivo: str = "") -> Requisicao:
    requisicao.status = StatusRequisicao.REJEITADA
    requisicao.aprovador = request.user
    requisicao.data_aprovacao = timezone.now()
    if motivo:
        requisicao.observacao = motivo
    requisicao.save()
    registrar_auditoria(
        request=request,
        acao="requisicao.rejeitar",
        entidade="requisicao",
        entidade_id=requisicao.id,
        detalhes={"motivo": motivo},
    )
    return requisicao


@transaction.atomic
def atender_requisicao_item(
    *,
    request,
    linha: RequisicaoItem,
    localizacao_origem_id: int,
    lote_id: int | None = None,
) -> RequisicaoItem:
    requisicao = linha.requisicao
    if requisicao.status != StatusRequisicao.APROVADA:
        raise ValidationError("Requisição precisa estar aprovada para atendimento.")
    qtd = linha.quantidade_aprovada or linha.quantidade_solicitada
    if qtd <= 0:
        raise ValidationError("Quantidade aprovada inválida.")

    lote = None
    if lote_id:
        lote = linha.item.lotes.filter(id=lote_id).first()
        if not lote:
            raise ValidationError("Lote não encontrado para o item.")

    registrar_movimentacao(
        request=request,
        item=linha.item,
        tipo_movimentacao=TipoMovimentacao.SAIDA,
        quantidade=Decimal(qtd),
        localizacao_origem_id=localizacao_origem_id,
        lote=lote,
        motivo=f"Atendimento requisição #{requisicao.id}",
        requisicao_item=linha,
    )
    linha.quantidade_atendida = qtd
    linha.save(update_fields=["quantidade_atendida"])

    if not requisicao.itens.filter(quantidade_atendida__isnull=True).exists():
        requisicao.status = StatusRequisicao.ATENDIDA
        requisicao.data_atendimento = timezone.now()
        requisicao.save(update_fields=["status", "data_atendimento"])

    registrar_auditoria(
        request=request,
        acao="requisicao.atender_item",
        entidade="requisicao_item",
        entidade_id=linha.id,
    )
    return linha
