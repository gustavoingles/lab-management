from django.contrib import admin
from .models import (
    PerfilUsuario, Categoria, Unidade, Localizacao, Item, Equipamento,
    Estoque, Movimentacao, Requisicao, RequisicaoItem, Reserva,
    OrdemServico, ManutencaoAgendada, Inventario, InventarioLinha, AuditoriaLog,
)

admin.site.register(PerfilUsuario)
admin.site.register(Categoria)
admin.site.register(Unidade)
admin.site.register(Localizacao)
admin.site.register(Item)
admin.site.register(Equipamento)
admin.site.register(Estoque)
admin.site.register(Movimentacao)
admin.site.register(Requisicao)
admin.site.register(RequisicaoItem)
admin.site.register(Reserva)
admin.site.register(OrdemServico)
admin.site.register(ManutencaoAgendada)
admin.site.register(Inventario)
admin.site.register(InventarioLinha)
admin.site.register(AuditoriaLog)
