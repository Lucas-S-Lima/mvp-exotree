from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Algorithm, ModelRun
from pipeline.training import train_random_forest


class Command(BaseCommand):
    help = "Treina o modelo Random Forest com os hiperparâmetros ótimos e registra as métricas no banco."

    def add_arguments(self, parser):
        parser.add_argument(
            "--n-estimators",
            type=int,
            default=200,
            help="Número de árvores na floresta.",
        )
        parser.add_argument(
            "--max-depth",
            type=int,
            default=30,
            help="Profundidade máxima das árvores.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=== Treinando Random Forest ==="))

        split_pkl = getattr(settings, "SPLIT_PKL_PATH", "data/exoplanets_split.pkl")
        model_path = getattr(settings, "RF_MODEL_PATH", "artifacts/rf_model.joblib")

        custom_params = {
            "n_estimators": options["n_estimators"],
            "max_depth": options["max_depth"],
        }

        model, metrics = train_random_forest(
            split_pkl_path=split_pkl,
            model_output_path=model_path,
            hyperparameters=custom_params,
        )

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
                f"Treinamento concluído!\n"
                f"ModelRun ID: {run_record.id}\n"
                f"Acurácia: {metrics['accuracy']:.4f}\n"
                f"F1-Macro: {metrics['f1_macro']:.4f}\n"
                f"Precisão: {metrics['precision_macro']:.4f}\n"
                f"Recall:   {metrics['recall_macro']:.4f}\n"
                f"OOB Score: {metrics.get('oob_score')}\n"
                f"Matriz de Confusão:\n"
                f"  VN: {metrics['true_negative']} | FP: {metrics['false_positive']}\n"
                f"  FN: {metrics['false_negative']} | VP: {metrics['true_positive']}\n"
                f"Artefato salvo em: {model_path}"
            )
        )

