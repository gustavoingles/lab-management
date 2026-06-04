from django.contrib import admin

from inventory import models

admin.site.register(models.Categoria)
admin.site.register(models.UnidadeMedida)
admin.site.register(models.Localizacao)
admin.site.register(models.Item)
admin.site.register(models.Equipamento)
admin.site.register(models.Estoque)
admin.site.register(models.Lote)
admin.site.register(models.Requisicao)
admin.site.register(models.RequisicaoItem)
admin.site.register(models.OrdemServico)
admin.site.register(models.Manutencao)
admin.site.register(models.Inventario)
admin.site.register(models.InventarioItem)
admin.site.register(models.Baixa)
admin.site.register(models.Movimentacao)
admin.site.register(models.Auditoria)
