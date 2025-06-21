# sisu/models.py

from django.db import models

class Nota(models.Model):
    # Campos de notas obrigatórios
    nota_matematica = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota Matemática")
    nota_linguagens = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota Linguagens")
    nota_humanas = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota Ciências Humanas")
    nota_natureza = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota Ciências da Natureza")
    nota_redacao = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota Redação")

    # Campos de dados do Sisu (assumindo que podem ser nulos inicialmente)
    CO_IES_CURSO = models.CharField(max_length=20, null=True, blank=True, verbose_name="Cód. IES Curso")
    CO_IES = models.CharField(max_length=10, null=True, blank=True, verbose_name="Cód. IES")
    DS_GRAU = models.CharField(max_length=50, null=True, blank=True, verbose_name="Grau")
    DS_TURNO = models.CharField(max_length=50, null=True, blank=True, verbose_name="Turno")
    DS_MOD_CONCORRENCIA = models.CharField(max_length=100, null=True, blank=True, verbose_name="Modalidade Concorrência")
    CO_CAMPUS = models.CharField(max_length=10, null=True, blank=True, verbose_name="Cód. Campus")
    SG_UF_CAMPUS = models.CharField(max_length=2, null=True, blank=True, verbose_name="UF Campus")

    # REMOVIDO: conteudo = models.TextField(null=True, blank=True, verbose_name="Conteúdo Adicional")
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            media = (self.nota_matematica + self.nota_linguagens + self.nota_humanas + self.nota_natureza + self.nota_redacao) / 5
            return f"Média: {media:.2f} | Curso: {self.CO_IES_CURSO or 'N/A'}"
        except TypeError:
            return f"Nota (ID: {self.id}) | Curso: {self.CO_IES_CURSO or 'N/A'}"

    class Meta:
        verbose_name = "Nota Sisu"
        verbose_name_plural = "Notas Sisu"