from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.models import Perfil, SolicitacaoAlteracaoPerfil, StatusSolicitacaoPerfil
from accounts.permissions import PERFIL_ADMIN, PERFIS_GESTAO, usuario_tem_perfil


def validar_nova_solicitacao(*, usuario, perfil_solicitado: Perfil, justificativa: str):
    if not justificativa.strip():
        raise ValidationError("Informe a justificativa.")
    if perfil_solicitado.pk == usuario.perfil_id:
        raise ValidationError("O perfil solicitado é o mesmo que o seu perfil atual.")
    if not perfil_solicitado.ativo:
        raise ValidationError("Este perfil não está disponível.")
    if SolicitacaoAlteracaoPerfil.objects.filter(
        solicitante=usuario,
        status=StatusSolicitacaoPerfil.PENDENTE,
    ).exists():
        raise ValidationError(
            "Você já possui uma solicitação pendente. Aguarde a análise do administrador."
        )


@transaction.atomic
def criar_solicitacao(*, usuario, perfil_solicitado: Perfil, justificativa: str):
    validar_nova_solicitacao(
        usuario=usuario,
        perfil_solicitado=perfil_solicitado,
        justificativa=justificativa,
    )
    return SolicitacaoAlteracaoPerfil.objects.create(
        solicitante=usuario,
        perfil_atual=usuario.perfil,
        perfil_solicitado=perfil_solicitado,
        justificativa=justificativa.strip(),
    )


def _pode_aprovar_perfil(revisor, perfil_destino: Perfil) -> bool:
    if revisor.is_superuser:
        return True
    if perfil_destino.codigo == PERFIL_ADMIN:
        return usuario_tem_perfil(revisor, PERFIL_ADMIN)
    return usuario_tem_perfil(revisor, *PERFIS_GESTAO)


@transaction.atomic
def aprovar_solicitacao(*, revisor, solicitacao: SolicitacaoAlteracaoPerfil, resposta: str = ""):
    if solicitacao.status != StatusSolicitacaoPerfil.PENDENTE:
        raise ValidationError("Esta solicitação já foi analisada.")
    if not _pode_aprovar_perfil(revisor, solicitacao.perfil_solicitado):
        raise ValidationError(
            "Você não tem permissão para aprovar este perfil. "
            "Apenas admin pode aprovar solicitação para perfil admin."
        )

    usuario = solicitacao.solicitante
    usuario.perfil = solicitacao.perfil_solicitado
    usuario.save(update_fields=["perfil"])

    solicitacao.status = StatusSolicitacaoPerfil.APROVADA
    solicitacao.revisado_por = revisor
    solicitacao.resposta_revisao = resposta.strip()
    solicitacao.revisada_em = timezone.now()
    solicitacao.save()

    try:
        from inventory.services.auditoria import registrar_auditoria

        registrar_auditoria(
            request=None,
            acao="solicitacao_perfil.aprovar",
            entidade="usuario",
            entidade_id=usuario.pk,
            detalhes={
                "perfil_anterior": solicitacao.perfil_atual.codigo,
                "perfil_novo": solicitacao.perfil_solicitado.codigo,
                "revisor_id": revisor.pk,
            },
        )
    except Exception:
        pass

    return solicitacao


@transaction.atomic
def rejeitar_solicitacao(
    *,
    revisor,
    solicitacao: SolicitacaoAlteracaoPerfil,
    resposta: str = "",
):
    if solicitacao.status != StatusSolicitacaoPerfil.PENDENTE:
        raise ValidationError("Esta solicitação já foi analisada.")
    if not usuario_tem_perfil(revisor, *PERFIS_GESTAO) and not revisor.is_superuser:
        raise ValidationError("Sem permissão para rejeitar solicitações.")

    solicitacao.status = StatusSolicitacaoPerfil.REJEITADA
    solicitacao.revisado_por = revisor
    solicitacao.resposta_revisao = resposta.strip()
    solicitacao.revisada_em = timezone.now()
    solicitacao.save()
    return solicitacao


@transaction.atomic
def cancelar_solicitacao(*, usuario, solicitacao: SolicitacaoAlteracaoPerfil):
    if solicitacao.solicitante_id != usuario.pk:
        raise ValidationError("Esta solicitação não é sua.")
    if solicitacao.status != StatusSolicitacaoPerfil.PENDENTE:
        raise ValidationError("Só é possível cancelar solicitações pendentes.")
    solicitacao.status = StatusSolicitacaoPerfil.CANCELADA
    solicitacao.revisada_em = timezone.now()
    solicitacao.save()
    return solicitacao
