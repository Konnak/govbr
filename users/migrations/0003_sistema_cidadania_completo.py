# Generated by Django 4.2.7 on 2025-06-19 19:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_user_discord_access_token_user_discord_avatar_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="solicitacaocidadania",
            options={
                "ordering": ["-data_solicitacao"],
                "permissions": [
                    (
                        "pode_analisar_cidadania",
                        "Pode analisar solicitações de cidadania",
                    ),
                    (
                        "pode_aprovar_cidadania",
                        "Pode aprovar solicitações de cidadania",
                    ),
                    (
                        "pode_configurar_cidadania",
                        "Pode configurar sistema de cidadania",
                    ),
                ],
                "verbose_name": "Solicitação de Cidadania",
                "verbose_name_plural": "Solicitações de Cidadania",
            },
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="analisado_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="cidadanias_analisadas",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Analisado Por",
            ),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="cep",
            field=models.CharField(blank=True, max_length=10, verbose_name="CEP"),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="cidade",
            field=models.CharField(blank=True, max_length=100, verbose_name="Cidade"),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="data_analise",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Data da Análise"
            ),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="data_aprovacao",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Data da Aprovação"
            ),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="data_nascimento",
            field=models.DateField(
                blank=True, null=True, verbose_name="Data de Nascimento"
            ),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="detalhes_criminal",
            field=models.TextField(
                blank=True,
                help_text="Se possui passagem criminal, detalhe aqui",
                verbose_name="Detalhes da Passagem Criminal",
            ),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="email",
            field=models.EmailField(blank=True, max_length=254, verbose_name="E-mail"),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="endereco",
            field=models.CharField(
                blank=True, max_length=300, verbose_name="Endereço Completo"
            ),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="estado",
            field=models.CharField(blank=True, max_length=50, verbose_name="Estado"),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="nacionalidade_origem",
            field=models.CharField(
                blank=True, max_length=100, verbose_name="Nacionalidade de Origem"
            ),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="nome_completo",
            field=models.CharField(
                blank=True, max_length=200, verbose_name="Nome Completo"
            ),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="nome_rp",
            field=models.CharField(
                blank=True, max_length=100, verbose_name="Nome no Roleplay"
            ),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="numero_protocolo",
            field=models.CharField(
                blank=True,
                help_text="Número único do protocolo da solicitação",
                max_length=20,
                unique=True,
                verbose_name="Número do Protocolo",
            ),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="observacoes_analise",
            field=models.TextField(
                blank=True,
                help_text="Observações do analista sobre a solicitação",
                verbose_name="Observações da Análise",
            ),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="possui_passagem_criminal",
            field=models.BooleanField(
                default=False,
                help_text="Marque se possui antecedentes criminais",
                verbose_name="Possui Passagem Criminal",
            ),
        ),
        migrations.AddField(
            model_name="solicitacaocidadania",
            name="telefone",
            field=models.CharField(blank=True, max_length=20, verbose_name="Telefone"),
        ),
        migrations.AlterField(
            model_name="solicitacaocidadania",
            name="status",
            field=models.CharField(
                choices=[
                    ("pendente", "Pendente"),
                    ("em_analise", "Em Análise"),
                    ("aprovada", "Aprovada"),
                    ("rejeitada", "Rejeitada"),
                    ("documentos_pendentes", "Documentos Pendentes"),
                ],
                default="pendente",
                max_length=20,
                verbose_name="Status",
            ),
        ),
        migrations.AlterField(
            model_name="solicitacaocidadania",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="solicitacoes_cidadania",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Usuário",
            ),
        ),
        migrations.CreateModel(
            name="HistoricoStatusCidadania",
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
                    "status_anterior",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("pendente", "Pendente"),
                            ("em_analise", "Em Análise"),
                            ("aprovada", "Aprovada"),
                            ("rejeitada", "Rejeitada"),
                            ("documentos_pendentes", "Documentos Pendentes"),
                        ],
                        max_length=20,
                        null=True,
                        verbose_name="Status Anterior",
                    ),
                ),
                (
                    "status_novo",
                    models.CharField(
                        choices=[
                            ("pendente", "Pendente"),
                            ("em_analise", "Em Análise"),
                            ("aprovada", "Aprovada"),
                            ("rejeitada", "Rejeitada"),
                            ("documentos_pendentes", "Documentos Pendentes"),
                        ],
                        max_length=20,
                        verbose_name="Status Novo",
                    ),
                ),
                (
                    "observacoes",
                    models.TextField(blank=True, verbose_name="Observações"),
                ),
                (
                    "data_mudanca",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data da Mudança"
                    ),
                ),
                (
                    "solicitacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="historico_status",
                        to="users.solicitacaocidadania",
                        verbose_name="Solicitação",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="historicos_cidadania",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuário Responsável",
                    ),
                ),
            ],
            options={
                "verbose_name": "Histórico de Status",
                "verbose_name_plural": "Históricos de Status",
                "ordering": ["-data_mudanca"],
            },
        ),
        migrations.CreateModel(
            name="DocumentoCidadania",
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
                    "tipo_documento",
                    models.CharField(
                        choices=[
                            ("rg", "RG"),
                            ("cnh", "CNH"),
                            ("cpf", "CPF"),
                            ("comprovante_residencia", "Comprovante de Residência"),
                            ("certidao_nascimento", "Certidão de Nascimento"),
                            ("passaporte", "Passaporte"),
                            ("outro", "Outro"),
                        ],
                        max_length=30,
                        verbose_name="Tipo de Documento",
                    ),
                ),
                (
                    "arquivo",
                    models.FileField(
                        help_text="Formatos aceitos: PDF, JPG, PNG, DOC, DOCX",
                        upload_to="cidadania/documentos/",
                        verbose_name="Arquivo",
                    ),
                ),
                (
                    "nome_original",
                    models.CharField(
                        max_length=255, verbose_name="Nome Original do Arquivo"
                    ),
                ),
                (
                    "descricao",
                    models.CharField(
                        blank=True,
                        help_text="Descrição adicional do documento",
                        max_length=200,
                        verbose_name="Descrição",
                    ),
                ),
                (
                    "validado",
                    models.BooleanField(
                        default=False,
                        help_text="Se o documento foi validado pelo analista",
                        verbose_name="Documento Validado",
                    ),
                ),
                (
                    "observacoes_validacao",
                    models.TextField(
                        blank=True, verbose_name="Observações da Validação"
                    ),
                ),
                (
                    "data_upload",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data do Upload"
                    ),
                ),
                (
                    "data_validacao",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Data da Validação"
                    ),
                ),
                (
                    "solicitacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documentos_anexos",
                        to="users.solicitacaocidadania",
                        verbose_name="Solicitação",
                    ),
                ),
                (
                    "validado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="documentos_validados",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Validado Por",
                    ),
                ),
            ],
            options={
                "verbose_name": "Documento de Cidadania",
                "verbose_name_plural": "Documentos de Cidadania",
                "ordering": ["tipo_documento", "data_upload"],
            },
        ),
    ]
