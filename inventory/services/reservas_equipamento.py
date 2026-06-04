from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.permissions import PERFIS_GESTAO, usuario_tem_perfil
from inventory.choices import StatusReservaEquipamento
from inventory.models import ReservaEquipamento


def _intervalo_invalido(inicio, fim) -> bool:
    return fim <= inicio


def _conflito_reserva(*, equipamento_id: int, inicio, fim, excluir_pk: int | None = None):
    qs = ReservaEquipamento.objects.filter(
        equipamento_id=equipamento_id,
        status__in=(
            StatusReservaEquipamento.PENDENTE,
            StatusReservaEquipamento.CONFIRMADA,
        ),
        inicio__lt=fim,
        fim__gt=inicio,
    )
    if excluir_pk:
        qs = qs.exclude(pk=excluir_pk)
    return qs.exists()


@transaction.atomic
def criar_reserva_equipamento(
    *,
    solicitante,
    equipamento_id: int,
    finalidade: str,
    inicio,
    fim,
    observacao: str = "",
) -> ReservaEquipamento:
    if _intervalo_invalido(inicio, fim):
        raise ValidationError("O horário de fim deve ser posterior ao início.")
    if not finalidade.strip():
        raise ValidationError("Informe a finalidade da reserva.")
    if _conflito_reserva(equipamento_id=equipamento_id, inicio=inicio, fim=fim):
        raise ValidationError(
            "Já existe reserva confirmada ou pendente neste intervalo para o equipamento."
        )
    return ReservaEquipamento.objects.create(
        equipamento_id=equipamento_id,
        solicitante=solicitante,
        finalidade=finalidade.strip(),
        inicio=inicio,
        fim=fim,
        observacao=observacao.strip(),
    )


@transaction.atomic
def aprovar_reserva_equipamento(*, revisor, reserva: ReservaEquipamento) -> ReservaEquipamento:
    if reserva.status != StatusReservaEquipamento.PENDENTE:
        raise ValidationError("Esta reserva já foi analisada.")
    if not usuario_tem_perfil(revisor, *PERFIS_GESTAO) and not revisor.is_superuser:
        raise ValidationError("Sem permissão para aprovar reservas de equipamento.")
    if _conflito_reserva(
        equipamento_id=reserva.equipamento_id,
        inicio=reserva.inicio,
        fim=reserva.fim,
        excluir_pk=reserva.pk,
    ):
        raise ValidationError("Conflito de horário com outra reserva ativa.")
    reserva.status = StatusReservaEquipamento.CONFIRMADA
    reserva.aprovador = revisor
    reserva.save(update_fields=["status", "aprovador", "atualizada_em"])
    return reserva


@transaction.atomic
def cancelar_reserva_equipamento(*, usuario, reserva: ReservaEquipamento) -> ReservaEquipamento:
    if reserva.status in (
        StatusReservaEquipamento.CANCELADA,
        StatusReservaEquipamento.ENCERRADA,
    ):
        raise ValidationError("Esta reserva já está encerrada ou cancelada.")
    pode_cancelar = (
        usuario.is_superuser
        or usuario_tem_perfil(usuario, *PERFIS_GESTAO)
        or reserva.solicitante_id == usuario.pk
    )
    if not pode_cancelar:
        raise ValidationError("Você não pode cancelar esta reserva.")
    reserva.status = StatusReservaEquipamento.CANCELADA
    reserva.save(update_fields=["status", "atualizada_em"])
    return reserva


@transaction.atomic
def encerrar_reserva_equipamento(*, reserva: ReservaEquipamento) -> ReservaEquipamento:
    if reserva.status != StatusReservaEquipamento.CONFIRMADA:
        raise ValidationError("Só reservas confirmadas podem ser encerradas.")
    reserva.status = StatusReservaEquipamento.ENCERRADA
    reserva.save(update_fields=["status", "atualizada_em"])
    return reserva


def reservas_ativas_equipamento(equipamento_id: int):
    agora = timezone.now()
    return ReservaEquipamento.objects.filter(
        equipamento_id=equipamento_id,
        status=StatusReservaEquipamento.CONFIRMADA,
        inicio__lte=agora,
        fim__gte=agora,
    )
