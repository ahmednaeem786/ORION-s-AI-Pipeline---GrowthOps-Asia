from .pipeline import OrionPipeline


if __name__ == "__main__":
    pipeline = OrionPipeline()
    result = pipeline.process_submission("data/mock_input/submission_coinbase.json")

    print("\n=======================================================")
    print("FINAL REVIEWER PAYLOAD (Emitted for Human Review)")
    print("=======================================================")
    print(result.model_dump_json(indent=2))
