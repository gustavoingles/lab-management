from django.http import HttpRequest

from inventory.models import Auditoria


def _client_ip(request: HttpRequest | None) -> str | None:
    if request is None:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def registrar_auditoria(
    *,
    request: HttpRequest | None,
    acao: str,
    entidade: str,
    entidade_id: int | None = None,
    detalhes: dict | None = None,
) -> Auditoria:
    usuario = request.user if request and request.user.is_authenticated else None
    return Auditoria.objects.create(
        usuario=usuario,
        acao=acao,
        entidade=entidade,
        entidade_id=entidade_id,
        detalhes=detalhes,
        ip_origem=_client_ip(request),
    )
