from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Algorithm, ModelRun
from pipeline.extraction import download_dataset
from pipeline.preprocessing import run_full_preprocessing
from pipeline.training import train_random_forest


class Command(BaseCommand):
    help = "Executa o pipeline completo: download/extração, pré-processamento, split e treino do Random Forest."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force-download",
            action="store_true",
            help="Força novo download da NASA mesmo se o arquivo local existir.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== Iniciando Pipeline Completo (mvp-exo) ==="))

        # 1. Extração
        self.stdout.write("1. Verificando dados da NASA...")
        raw_csv = getattr(settings, "RAW_CSV_PATH", "data/cumulative_koi.csv")
        download_dataset(output_path=raw_csv, force_download=options["force_download"])

        # 2. Pré-processamento
        self.stdout.write("2. Executando limpeza, transformações e split...")
        treated_csv = getattr(settings, "TREATED_CSV_PATH", "data/cumulative_koi_treated.csv")
        split_pkl = getattr(settings, "SPLIT_PKL_PATH", "data/exoplanets_split.pkl")
        scaler_path = getattr(settings, "SCALER_PATH", "artifacts/scaler.joblib")

        run_full_preprocessing(
            raw_csv_path=raw_csv,
            output_treated_csv=treated_csv,
            output_split_pkl=split_pkl,
            output_scaler_path=scaler_path,
        )

        # 3. Treinamento
        self.stdout.write("3. Treinando modelo Random Forest otimizado...")
        model_path = getattr(settings, "RF_MODEL_PATH", "artifacts/rf_model.joblib")
        model, metrics = train_random_forest(
            split_pkl_path=split_pkl,
            model_output_path=model_path,
        )

        # 4. Registro no banco de dados
        algo, _ = Algorithm.objects.get_or_create(algorithm="random_forest")
        run_record = ModelRun.objects.create(
            algorithm=algo,
            accuracy=metrics["accuracy"],
            precision=metrics["precision_macro"],
            recall=metrics["recall_macro"],
            f1_score=metrics["f1_macro"],
            true_positive=metrics["true_positive"],
            true_negative=metrics["true_negative"],
            false_positive=metrics["false_positive"],
            false_negative=metrics["false_negative"],
            hyperparameters=model.get_params(),
            model_artifact_path=str(model_path),
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nPipeline finalizado com sucesso!\n"
                f"ModelRun ID: {run_record.id}\n"
                f"Acurácia: {metrics['accuracy']:.4f}\n"
                f"F1 Macro: {metrics['f1_macro']:.4f}\n"
                f"Artefato salvo em: {model_path}"
            )
        )

