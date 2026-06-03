from app.models.codeFile import CodeFile
from sqlalchemy.orm import Session

class CodeFileRepository:

    @staticmethod
    def create(db, data):
        exists = CodeFileRepository.exists(db, data["file_id"])
        if exists:
            print("Data alreay exists")
            return exists
        codeFile = CodeFile(**data)
        print("Creating CodeFile:", data["file_id"])

        codeFile = CodeFile(**data)

        db.add(codeFile)

        print("Before commit")

        db.commit()

        print("After commit")

        db.refresh(codeFile)

        return codeFile

    @staticmethod
    def exists(db: Session, file_id):
        return db.query(CodeFile).filter(CodeFile.file_id == file_id).first()
    