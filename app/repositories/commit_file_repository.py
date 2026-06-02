from app.models.commitFile import CommitFile

class CommitFileRepository:
    @staticmethod
    def create(db, data):
        relation = CommitFile(**data)

        db.add(relation)
        return relation