from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from inventory.choices import StatusOperacional, StatusOrdemServico
from inventory.models import OrdemServico
from inventory.services.auditoria import registrar_auditoria


@transaction.atomic
def iniciar_ordem_servico(*, request, ordem: OrdemServico) -> OrdemServico:
    if ordem.status != StatusOrdemServico.ABERTA:
        raise ValidationError("Ordem de serviço não está aberta.")
    ordem.status = StatusOrdemServico.EM_EXECUCAO
    ordem.inicio_execucao_em = timezone.now()
    ordem.tecnico_responsavel = request.user
    ordem.save()
    equip = ordem.equipamento
    equip.status_operacional = StatusOperacional.EM_MANUTENCAO
    equip.save(update_fields=["status_operacional", "updated_at"])
    registrar_auditoria(
        request=request,
        acao="ordem_servico.iniciar",
        entidade="ordem_servico",
        entidade_id=ordem.id,
    )
    return ordem


@transaction.atomic
def encerrar_ordem_servico(
    *,
    request,
    ordem: OrdemServico,
    laudo_emitido: bool = False,
    status_equipamento: str = StatusOperacional.ATIVO,
) -> OrdemServico:
    if ordem.status not in (
        StatusOrdemServico.EM_EXECUCAO,
        StatusOrdemServico.AGUARDANDO_PECAS,
    ):
        raise ValidationError("Ordem de serviço não está em execução.")
    ordem.status = StatusOrdemServico.ENCERRADA
    ordem.encerrada_em = timezone.now()
    ordem.laudo_emitido = laudo_emitido
    ordem.save()
    equip = ordem.equipamento
    equip.status_operacional = status_equipamento
    equip.save(update_fields=["status_operacional", "updated_at"])
    registrar_auditoria(
        request=request,
        acao="ordem_servico.encerrar",
        entidade="ordem_servico",
        entidade_id=ordem.id,
        detalhes={"laudo_emitido": laudo_emitido},
    )
    return ordem
