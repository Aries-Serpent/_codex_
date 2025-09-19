
from fastapi import HTTPException, status

def enforce_confirmation(confirm: bool | None, dry_run: bool | None):
    # All destructive operations require confirm==True unless dry_run==True
    if dry_run:
        return
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Destructive action requires confirm=true or use dry_run=true.",
        )
