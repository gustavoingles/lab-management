"""
Populate the database with the demo data from the LabManager prototype.
Run: uv run python manage.py seed_db
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from core.models import (
    PerfilUsuario, Categoria, Unidade, Localizacao, Item, Equipamento,
    Estoque, Movimentacao, Requisicao, RequisicaoItem, Reserva,
    OrdemServico, ManutencaoAgendada, Inventario, InventarioLinha, AuditoriaLog,
)

TZ = ZoneInfo("America/Maceio")
PASSWORD = "labtest"


def make_dt(day_offset, hour, minute=0):
    base = date(2026, 6, 5)
    d = base + timedelta(days=day_offset)
    return datetime(d.year, d.month, d.day, hour, minute, tzinfo=TZ)


class Command(BaseCommand):
    help = "Seed the database with LabManager demo data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # ---- users -----------------------------------------------------------
        users = {}
        user_data = [
            ("claudia@lab.test", "claudia", "Cláudia", "Souza", "gestor", "CS"),
            ("renato@lab.test", "renato", "Renato", "Lima", "almoxarife", "RL"),
            ("marina@lab.test", "marina", "Marina", "Alves", "solicitante", "MA"),
            ("iuri@lab.test", "iuri", "Iuri", "Mendes", "manutencao", "IM"),
            ("joao@lab.test", "joao", "João", "Pereira", "solicitante", "JP"),
            ("ana@lab.test", "ana", "Ana", "Costa", "solicitante", "AC"),
        ]
        for email, username, first, last, role, iniciais in user_data:
            u, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "first_name": first, "last_name": last},
            )
            if created:
                u.set_password(PASSWORD)
                u.save()
            PerfilUsuario.objects.get_or_create(usuario=u, defaults={"role": role, "iniciais": iniciais})
            users[username] = u
        self.stdout.write(f"  {len(users)} users ok")

        # ---- categorias ------------------------------------------------------
        cats = {}
        for codigo, nome in [("REAG", "Reagentes"), ("CONS", "Consumíveis"), ("EPI", "Proteção individual"), ("EQUIP", "Equipamentos"), ("PECA", "Peças e sobressalentes")]:
            c, _ = Categoria.objects.get_or_create(codigo=codigo, defaults={"nome": nome})
            cats[codigo] = c

        # ---- unidades --------------------------------------------------------
        unis = {}
        for sigla, nome in [("mL", "Mililitro"), ("L", "Litro"), ("un", "Unidade"), ("cx", "Caixa"), ("par", "Par")]:
            u, _ = Unidade.objects.get_or_create(sigla=sigla, defaults={"nome": nome})
            unis[sigla] = u

        # ---- localizações ----------------------------------------------------
        locs = {}
        campus, _ = Localizacao.objects.get_or_create(nome="Campus Saúde", defaults={"tipo": "campus", "pai": None})
        locs["campus"] = campus
        predio, _ = Localizacao.objects.get_or_create(nome="Prédio A — Biológicas", defaults={"tipo": "predio", "pai": campus})
        locs["predio"] = predio
        for nome, tipo, pai_key in [
            ("Lab. Bioquímica", "laboratorio", "predio"),
            ("Lab. Microbiologia", "laboratorio", "predio"),
            ("Almoxarifado Central", "armario", "predio"),
        ]:
            l, _ = Localizacao.objects.get_or_create(nome=nome, defaults={"tipo": tipo, "pai": locs[pai_key]})
            locs[nome] = l
        armario, _ = Localizacao.objects.get_or_create(nome="Armário B2", defaults={"tipo": "armario", "pai": locs["Lab. Bioquímica"]})
        locs["Armário B2"] = armario

        # ---- itens -----------------------------------------------------------
        itens = {}
        item_data = [
            ("REAG-001", "Etanol 70%", "reagente", "REAG", "mL", False),
            ("REAG-002", "Ácido Clorídrico PA", "reagente", "REAG", "mL", True),
            ("REAG-003", "Solução de Lugol", "reagente", "REAG", "mL", False),
            ("CONS-001", "Ponteira 1000 µL", "consumivel", "CONS", "un", False),
            ("CONS-002", "Tubo Falcon 15 mL", "consumivel", "CONS", "un", False),
            ("EPI-001", "Luva Nitrílica M", "epi", "EPI", "cx", False),
            ("EPI-002", "Óculos de proteção", "epi", "EPI", "un", False),
            ("EQ-001", "Microscópio Binocular", "equipamento", "EQUIP", "un", False),
            ("EQ-002", "Centrífuga Refrigerada", "equipamento", "EQUIP", "un", False),
            ("EQ-003", "Autoclave Vertical", "equipamento", "EQUIP", "un", False),
            ("PECA-001", "Rotor para centrífuga", "peca", "PECA", "un", False),
        ]
        for codigo, nome, tipo, cat_key, uni_key, controlado in item_data:
            it, _ = Item.objects.get_or_create(
                codigo=codigo,
                defaults={"nome": nome, "tipo": tipo, "categoria": cats[cat_key], "unidade": unis[uni_key], "controlado": controlado},
            )
            itens[codigo] = it

        # ---- equipamentos ----------------------------------------------------
        equips = {}
        equip_data = [
            ("MIC-2021-0098", "TB-44210", "EQ-001", "ativo", "Lab. Bioquímica", date(2021, 3, 12)),
            ("CEN-2019-0312", "TB-39817", "EQ-002", "em_manutencao", "Lab. Microbiologia", date(2019, 7, 30)),
            ("AUT-2022-0011", "TB-50120", "EQ-003", "ativo", "Lab. Microbiologia", date(2022, 11, 5)),
            ("MIC-2017-0044", "TB-28890", "EQ-001", "inativo", "Almoxarifado Central", date(2017, 2, 18)),
        ]
        for serie, tomb, item_key, status, local_nome, aquisicao in equip_data:
            eq, _ = Equipamento.objects.get_or_create(
                serie=serie,
                defaults={"tombamento": tomb, "item": itens[item_key], "status": status, "localizacao": locs[local_nome], "aquisicao": aquisicao},
            )
            equips[serie] = eq

        # ---- estoque ---------------------------------------------------------
        estoque_data = [
            ("REAG-001", "Lab. Bioquímica", 5000, 500, 1000, 1500),
            ("REAG-002", "Almoxarifado Central", 2000, 0, 500, 800),
            ("CONS-001", "Almoxarifado Central", 120, 100, 50, 80),
            ("CONS-002", "Lab. Microbiologia", 40, 10, 25, 30),
            ("EPI-001", "Lab. Microbiologia", 8, 0, 5, 6),
            ("REAG-003", "Armário B2", 250, 0, 100, 150),
        ]
        for item_key, local_nome, total, reservado, minimo, alerta in estoque_data:
            Estoque.objects.get_or_create(
                item=itens[item_key],
                localizacao=locs[local_nome],
                defaults={"total": total, "reservado": reservado, "minimo": minimo, "alerta": alerta},
            )

        # ---- ordens de serviço -----------------------------------------------
        ordens = {}
        os_data = [
            (205, equips["CEN-2019-0312"], "Ruído anormal e vibração acima do esperado no rotor.", "alta", "em_execucao", users["iuri"], date(2026, 6, 3)),
            (204, equips["AUT-2022-0011"], "Calibração de pressão pendente (vencida).", "media", "aberta", None, date(2026, 6, 4)),
            (201, equips["MIC-2021-0098"], "Troca de lâmpada de iluminação.", "baixa", "encerrada", users["iuri"], date(2026, 5, 20)),
            (198, equips["CEN-2019-0312"], "Falha no sistema de refrigeração.", "critica", "encerrada", users["iuri"], date(2026, 5, 2)),
        ]
        for _, equip, desc, prio, stat, resp, aber in os_data:
            os_obj, created = OrdemServico.objects.get_or_create(
                equipamento=equip,
                descricao=desc,
                defaults={"prioridade": prio, "status": stat, "responsavel": resp},
            )
            if created:
                OrdemServico.objects.filter(pk=os_obj.pk).update(abertura=aber)
                os_obj.refresh_from_db()
            ordens[os_obj.equipamento.serie + "_" + stat] = os_obj

        os205 = OrdemServico.objects.filter(equipamento=equips["CEN-2019-0312"], status="em_execucao").first()
        os201 = OrdemServico.objects.filter(equipamento=equips["MIC-2021-0098"], status="encerrada").first()
        os198 = OrdemServico.objects.filter(equipamento=equips["CEN-2019-0312"], status="encerrada").first()

        # ---- manutenções agendadas -------------------------------------------
        man_data = [
            (equips["MIC-2021-0098"], "corretiva", date(2026, 5, 20), date(2026, 11, 20), os201),
            (equips["CEN-2019-0312"], "corretiva", date(2026, 5, 5), None, os198),
            (equips["AUT-2022-0011"], "calibracao", date(2026, 2, 1), date(2026, 6, 1), None),
            (equips["MIC-2021-0098"], "preventiva", date(2026, 2, 10), date(2026, 8, 10), None),
        ]
        for equip, tipo, realizada, proxima, ordem in man_data:
            ManutencaoAgendada.objects.get_or_create(
                equipamento=equip,
                tipo=tipo,
                defaults={"ultima_realizada": realizada, "proxima": proxima, "ordem": ordem},
            )

        # ---- requisições -----------------------------------------------------
        req1042, _ = Requisicao.objects.get_or_create(
            finalidade="Aula prática de Bioquímica — Turma B",
            defaults={
                "justificativa": "Material para 24 alunos na bancada de extração.",
                "solicitante": users["marina"],
                "status": "aberta",
                "prioridade": "media",
            },
        )
        Requisicao.objects.filter(pk=req1042.pk).update(criada=date(2026, 6, 5))
        for item_key, qtd, uni_key in [("REAG-001", 500, "mL"), ("CONS-001", 50, "un"), ("CONS-002", 20, "un")]:
            RequisicaoItem.objects.get_or_create(
                requisicao=req1042, item=itens[item_key],
                defaults={"unidade": unis[uni_key], "solicitado": qtd},
            )

        req1041, _ = Requisicao.objects.get_or_create(
            finalidade="Cultura microbiológica",
            defaults={
                "justificativa": "Reposição semanal.",
                "solicitante": users["marina"],
                "status": "aprovada",
                "prioridade": "media",
                "aprovador": users["claudia"],
            },
        )
        Requisicao.objects.filter(pk=req1041.pk).update(criada=date(2026, 6, 4))
        ri1041, _ = RequisicaoItem.objects.get_or_create(
            requisicao=req1041, item=itens["EPI-001"],
            defaults={"unidade": unis["cx"], "solicitado": 2, "aprovado": 2, "reserva_local": locs["Lab. Microbiologia"]},
        )

        req1039, _ = Requisicao.objects.get_or_create(
            finalidade="Preparo de meio de cultura",
            defaults={"solicitante": users["joao"], "status": "atendida", "prioridade": "media"},
        )
        Requisicao.objects.filter(pk=req1039.pk).update(criada=date(2026, 6, 3))

        req1038, _ = Requisicao.objects.get_or_create(
            finalidade="Teste de bancada",
            defaults={"solicitante": users["marina"], "status": "rejeitada", "prioridade": "baixa", "aprovador": users["claudia"]},
        )
        Requisicao.objects.filter(pk=req1038.pk).update(criada=date(2026, 6, 1))

        req1035, _ = Requisicao.objects.get_or_create(
            finalidade="Análise de amostras",
            defaults={"solicitante": users["ana"], "status": "atendida", "prioridade": "media"},
        )
        Requisicao.objects.filter(pk=req1035.pk).update(criada=date(2026, 5, 28))

        # ---- reservas --------------------------------------------------------
        reserva_data = [
            (equips["MIC-2021-0098"], users["marina"], make_dt(1, 14), make_dt(1, 16), "pendente", "Análise de lâminas"),
            (equips["AUT-2022-0011"], users["joao"], make_dt(1, 9), make_dt(1, 10, 30), "confirmada", "Esterilização de vidraria"),
            (equips["MIC-2021-0098"], users["ana"], make_dt(2, 10), make_dt(2, 12), "confirmada", "Contagem celular"),
            (equips["AUT-2022-0011"], users["marina"], make_dt(0, 16), make_dt(0, 17), "encerrada", "Descontaminação"),
        ]
        for equip, sol, inicio, fim, stat, finalidade in reserva_data:
            Reserva.objects.get_or_create(
                equipamento=equip,
                solicitante=sol,
                inicio=inicio,
                defaults={"fim": fim, "status": stat, "finalidade": finalidade},
            )

        # ---- movimentações ---------------------------------------------------
        mov_data = [
            ("saida", "CONS-001", None, "Almoxarifado Central", 80, users["renato"], "REQ #1039"),
            ("entrada", "REAG-001", None, "Lab. Bioquímica", 2000, users["renato"], "NF 8841"),
            ("transferencia", "CONS-002", "Almoxarifado Central", "Lab. Microbiologia", 20, users["renato"], ""),
            ("ajuste", "EPI-001", None, "Lab. Microbiologia", 8, users["claudia"], "INV-2026-03"),
            ("entrada", "REAG-002", None, "Almoxarifado Central", 2000, users["renato"], "NF 8830"),
            ("baixa", "REAG-003", "Armário B2", None, 50, users["claudia"], "Validade"),
        ]
        for tipo, item_key, orig_nome, dest_nome, qtd, usr, ref in mov_data:
            orig = locs[orig_nome] if orig_nome else None
            dest = locs[dest_nome] if dest_nome else None
            if not Movimentacao.objects.filter(tipo=tipo, item=itens[item_key], referencia=ref).exists():
                Movimentacao.objects.create(
                    tipo=tipo, item=itens[item_key], origem=orig, destino=dest,
                    quantidade=qtd, usuario=usr, referencia=ref,
                )

        # ---- inventários -----------------------------------------------------
        inv_data = [
            ("INV-2026-03", "Lab. Microbiologia", users["renato"], "em_andamento", date(2026, 6, 3)),
            ("INV-2026-02", "Almoxarifado Central", users["renato"], "encerrado", date(2026, 5, 1)),
            ("INV-2026-01", "Lab. Bioquímica", users["claudia"], "encerrado", date(2026, 4, 2)),
        ]
        invs = {}
        for codigo, local_nome, resp, stat, criado in inv_data:
            inv, _ = Inventario.objects.get_or_create(
                codigo=codigo,
                defaults={"localizacao": locs[local_nome], "responsavel": resp, "status": stat},
            )
            if _:
                Inventario.objects.filter(pk=inv.pk).update(criado=criado)
            invs[codigo] = inv

        inv_linhas = [
            ("CONS-002", "Lab. Microbiologia", 40, 38),
            ("EPI-001", "Lab. Microbiologia", 8, 8),
            ("CONS-001", "Lab. Microbiologia", 0, 12),
            ("REAG-003", "Armário B2", 250, 250),
        ]
        for item_key, local_nome, esperado, contado in inv_linhas:
            InventarioLinha.objects.get_or_create(
                inventario=invs["INV-2026-03"],
                item=itens[item_key],
                defaults={"localizacao": locs[local_nome], "esperado": esperado, "contado": contado},
            )

        # ---- auditoria -------------------------------------------------------
        audit_data = [
            (users["claudia"], "aprovou", "Requisição #1041", "check-circle-2", "success", make_dt(0, 9, 14)),
            (users["renato"], "registrou saída de", "Ponteira 1000 µL (80 un)", "arrow-up-from-line", "info", make_dt(-1, 14, 22)),
            (users["renato"], "registrou entrada de", "Etanol 70% (2000 mL)", "arrow-down-to-line", "success", make_dt(-1, 11, 8)),
            (users["marina"], "criou", "Requisição #1042", "file-plus", "neutral", make_dt(-1, 8, 50)),
            (users["renato"], "transferiu", "Tubo Falcon 15 mL (20 un)", "arrow-left-right", "info", make_dt(-2, 16, 45)),
            (users["iuri"], "abriu", "OS #205 — Centrífuga", "wrench", "amber", make_dt(-2, 10, 2)),
            (users["renato"], "registrou entrada de", "Ácido Clorídrico PA (2000 mL)", "arrow-down-to-line", "success", make_dt(-3, 15, 12)),
            (users["claudia"], "rejeitou", "Requisição #1038", "x-circle", "destructive", make_dt(-4, 17, 30)),
        ]
        if AuditoriaLog.objects.count() == 0:
            for usr, acao, alvo, icon, tone, quando in audit_data:
                log = AuditoriaLog.objects.create(
                    usuario=usr, acao=acao, alvo=alvo, icon=icon, tone=tone,
                )
                AuditoriaLog.objects.filter(pk=log.pk).update(quando=quando)

        self.stdout.write(self.style.SUCCESS("Database seeded successfully."))
        self.stdout.write(f"  Login: claudia@lab.test / {PASSWORD}  (gestor)")
        self.stdout.write(f"  Login: renato@lab.test / {PASSWORD}  (almoxarife)")
        self.stdout.write(f"  Login: marina@lab.test / {PASSWORD}  (solicitante)")
        self.stdout.write(f"  Login: iuri@lab.test   / {PASSWORD}  (manutencao)")
