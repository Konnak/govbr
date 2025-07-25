# Generated by Django 4.2.7 on 2025-06-19 19:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0011_fix_duplicacao_diario"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConfiguracaoCidadania",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "prazo_analise_dias",
                    models.PositiveIntegerField(
                        default=7,
                        help_text="Prazo padrão em dias para análise das solicitações",
                        verbose_name="Prazo para Análise (Dias)",
                    ),
                ),
                (
                    "documentos_obrigatorios",
                    models.TextField(
                        default="RG ou CNH\nCPF\nComprovante de Residência",
                        help_text="Lista de documentos obrigatórios (um por linha)",
                        verbose_name="Documentos Obrigatórios",
                    ),
                ),
                (
                    "instrucoes",
                    models.TextField(
                        default="Para solicitar sua cidadania brasileira, preencha o formulário abaixo com seus dados pessoais e anexe os documentos necessários.",
                        help_text="Instruções exibidas na página de solicitação",
                        verbose_name="Instruções",
                    ),
                ),
                (
                    "ativo",
                    models.BooleanField(
                        default=True,
                        help_text="Se o sistema de cidadania está aceitando novas solicitações",
                        verbose_name="Sistema Ativo",
                    ),
                ),
                ("data_criacao", models.DateTimeField(auto_now_add=True)),
                ("data_atualizacao", models.DateTimeField(auto_now=True)),
                (
                    "cargos_autorizados",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Cargos que podem aprovar/rejeitar solicitações de cidadania",
                        to="main.cargo",
                        verbose_name="Cargos Autorizados",
                    ),
                ),
                (
                    "orgao_responsavel",
                    models.ForeignKey(
                        blank=True,
                        help_text="Órgão responsável pelo processamento de solicitações de cidadania",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="main.orgao",
                        verbose_name="Órgão Responsável",
                    ),
                ),
            ],
            options={
                "verbose_name": "Configuração de Cidadania",
                "verbose_name_plural": "Configurações de Cidadania",
            },
        ),
    ]
