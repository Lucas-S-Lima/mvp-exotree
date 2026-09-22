from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.gridsearch import run_random_forest_gridsearch


class Command(BaseCommand):
    help = "Executa busca de hiperparâmetros (GridSearchCV) para o Random Forest."

    def add_arguments(self, parser):
        parser.add_argument(
            "--quick",
            action="store_true",
            help="Executa versão rápida com número reduzido de combinações (ideal para testes).",
        )
        parser.add_argument(
            "--cv-splits",
            type=int,
            default=5,
            help="Número de folds da validação cruzada (padrão: 5).",
        )
        parser.add_argument(
            "--n-jobs",
            type=int,
            default=-1,
            help="Número de jobs paralelos (padrão: -1 para usar todas as CPUs).",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=== Iniciando GridSearch para Random Forest ==="))

        split_pkl = getattr(settings, "SPLIT_PKL_PATH", "data/exoplanets_split.pkl")
        quick = options["quick"]
        cv_splits = options["cv_splits"]
        n_jobs = options["n_jobs"]

        results = run_random_forest_gridsearch(
            split_pkl_path=split_pkl,
            quick=quick,
            cv_splits=cv_splits,
            n_jobs=n_jobs,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nGridSearch concluído em {results['elapsed_time_seconds']:.2f} s!\n"
                f"Total de combinações avaliadas: {results['total_combinations']}\n"
                f"Melhor F1-Macro: {results['best_score']:.4f}\n"
                f"Melhores Parâmetros:\n{results['best_params']}\n"
            )
        )
        self.stdout.write("Top 5 configurações:")
        for idx, cfg in enumerate(results["top_configurations"], 1):
            self.stdout.write(
                f" {idx}. F1-Macro: {cfg['mean_test_f1_macro']:.4f} "
                f"(Std: {cfg['std_test_f1_macro']:.4f}) | Params: {cfg['params']}"
            )

