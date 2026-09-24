"""Comando para entrenar el clasificador supervisado modelomainv1."""

import argparse

from app.database import SessionLocal
from app.training import train_model


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Entrena modelomainv1 con categorizaciones manuales"
    )
    parser.add_argument(
        "--output",
        default="models/modelomainv1.pkl",
        help="ruta donde guardar el modelo entrenado",
    )
    parser.add_argument(
        "--validation-size",
        type=float,
        default=0.2,
        help="proporcion de ejemplos reservada para validacion",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        report = train_model(
            db,
            model_path=args.output,
            validation_size=args.validation_size,
        )
    finally:
        db.close()

    print(f"Modelo guardado: {report.model_path}")
    print(f"Ejemplos de entrenamiento: {report.training_examples}")
    print(f"Ejemplos de validacion: {report.validation_examples}")
    print(f"Accuracy: {report.metrics['accuracy']:.2%}")


if __name__ == "__main__":
    main()