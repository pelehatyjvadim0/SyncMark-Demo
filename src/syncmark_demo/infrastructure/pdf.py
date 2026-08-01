from pathlib import Path

from reportlab.pdfgen.canvas import Canvas


class SyntheticLabelGenerator:
    def __init__(self, directory: str = "generated-labels") -> None:
        self.directory = Path(directory)

    def generate(self, shipment_id: str) -> str:
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.directory / f"{shipment_id}.pdf"
        canvas = Canvas(str(path))
        canvas.drawString(72, 720, f"Synthetic SyncMark Demo Label: {shipment_id}")
        canvas.save()
        return f"/labels/{shipment_id}.pdf"
