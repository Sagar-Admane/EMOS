from sqlalchemy.orm import Session

from app.models.branch import Branch

class BrachRepository:

    @staticmethod
    def get_by_name(db: Session, repo_id: int, name: str):
        return db.query(Branch).filter(Branch.repo_id==repo_id, Branch.name == name)

    @staticmethod
    def create(db: Session, data: dict):
        existing = BrachRepository.get_by_name(db, data["repo_id"], data["name"]).first()
        if existing:
            print("Existing exists")
            return existing
        
        branch = Branch(**data)

        print("Saving data to db")

        db.add(branch)
        db.commit()
        db.refresh(branch)

        print("Created ID: ", branch.id)

        return branch