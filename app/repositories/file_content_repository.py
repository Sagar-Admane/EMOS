from app.models.file_contents import FileContent
from sqlalchemy.orm import Session

class FileContentRepository:

    @staticmethod
    def create(db: Session, data: dict):
        content = FileContent(**data)

        db.add(content)
        db.commit()
        db.refresh(content)

        return content

    @staticmethod
    def get_by_file_id(db: Session, file_id: int):
        return db.query(FileContent).filter(FileContent.file_id == file_id).first()

    @staticmethod
    def update(db:Session, data: dict):
        file_content = FileContentRepository.get_by_file_id(db,data["file_id"])

        file_content.content = data["content"]
        file_content.content_hashed = data["content_hashed"]

        db.commit()
        db.refresh(file_content)

        return fi


