from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import select
from typing_extensions import TypedDict

from connection import init_db, get_session
from models import *

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def hello():
    return "Hello, [username]!"


@app.post("/warrior")
def warriors_create(warrior: WarriorDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                                     "data": Warrior}):
    warrior = Warrior.model_validate(warrior)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return {"status": 200, "data": warrior}


@app.get("/warriors_list")
def warriors_list(session=Depends(get_session)) -> List[Warrior]:
    return session.exec(select(Warrior)).all()


@app.get("/warrior/{warrior_id}", response_model=WarriorWithFullDetails)
def warriors_get(warrior_id: int, session=Depends(get_session)) -> Warrior:
    warrior = session.get(Warrior, warrior_id)
    return warrior

@app.patch("/warrior/{warrior_id}")
def warrior_update(warrior_id: int, warrior: WarriorDefault, session=Depends(get_session)) -> WarriorDefault:
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    warrior_data = warrior.model_dump(exclude_unset=True)
    for key, value in warrior_data.items():
        setattr(db_warrior, key, value)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior


@app.delete("/warrior/delete/{warrior_id}")
def warrior_delete(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}


@app.post("/warrior/{warrior_id}/add_skill/{skill_id}")
def add_skill_to_warrior(warrior_id: int, skill_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    skill = session.get(Skill, skill_id)

    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    if skill in warrior.skills:
        raise HTTPException(status_code=400, detail="Skill is already linked to the warrior")

    warrior.skills.append(skill)
    session.commit()
    session.refresh(warrior)

    return {"status": 200, "message": f"Skill '{skill.name}' added to warrior '{warrior.name}'"}


@app.get("/professions_list")
def professions_list(session=Depends(get_session)) -> List[Profession]:
    return session.exec(select(Profession)).all()


@app.get("/profession/{profession_id}")
def profession_get(profession_id: int, session=Depends(get_session)) -> Profession:
    return session.get(Profession, profession_id)


@app.post("/profession")
def profession_create(prof: ProfessionDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                                       "data": Profession}):
    prof = Profession.model_validate(prof)
    session.add(prof)
    session.commit()
    session.refresh(prof)
    return {"status": 200, "data": prof}


@app.get("/skills_list")
def skills_list(session=Depends(get_session)) -> List[Skill]:
    return session.exec(select(Skill)).all()


@app.post("/skill")
def skill_create(skill: Skill, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                       "data": Skill}):
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return {"status": 200, "data": skill}


@app.get("/skill/{skill_id}")
def skill_get(skill_id: int, session=Depends(get_session)) -> Skill:
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@app.patch("/skill/{skill_id}")
def skill_update(skill_id: int, skill: Skill, session=Depends(get_session)) -> Skill:
    db_skill = session.get(Skill, skill_id)
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    skill_data = skill.model_dump(exclude_unset=True)
    for key, value in skill_data.items():
        setattr(db_skill, key, value)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill


@app.delete("/skill/delete/{skill_id}")
def skill_delete(skill_id: int, session=Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    session.delete(skill)
    session.commit()
    return {"ok": True}
