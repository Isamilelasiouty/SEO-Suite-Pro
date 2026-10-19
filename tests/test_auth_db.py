"""
Unit tests for database persistence, bcrypt password hashing, user registration, and per-user data isolation.
"""

from core.database import (
    authenticate_user,
    delete_analysis,
    get_analysis_by_id,
    get_user_analyses,
    hash_password,
    init_db,
    register_user,
    save_analysis,
)

def test_user_lifecycle_and_isolation():
    import uuid
    init_db()
    
    uid = uuid.uuid4().hex[:6]
    # 1. Register User A
    ok, _ = register_user(f"usera_{uid}", f"usera_{uid}@test.com", "PasswordA123")
    assert ok is True
    user_a = authenticate_user(f"usera_{uid}", "PasswordA123")
    assert user_a is not None
    
    # 2. Register User B
    ok_b, _ = register_user(f"userb_{uid}", f"userb_{uid}@test.com", "PasswordB123")
    assert ok_b is True
    user_b = authenticate_user(f"userb_{uid}", "PasswordB123")
    assert user_b is not None
    
    # 3. Save analysis under User A
    a_id = save_analysis(user_a["id"], "onpage", "https://site-a.com", {"score": 85}, {"full": True})
    assert a_id > 0
    
    # 4. Verify User A sees it
    user_a_analyses = get_user_analyses(user_a["id"])
    assert any(a["id"] == a_id for a in user_a_analyses)
    
    # 5. Verify User B CANNOT see User A's analysis (Strict Isolation)
    user_b_analyses = get_user_analyses(user_b["id"])
    assert not any(a["id"] == a_id for a in user_b_analyses)
    
    # 6. Verify User B cannot fetch User A's analysis by ID
    forbidden_fetch = get_analysis_by_id(a_id, user_b["id"])
    assert forbidden_fetch is None
    
    # 7. Delete analysis by owner
    assert delete_analysis(a_id, user_a["id"]) is True
    assert get_analysis_by_id(a_id, user_a["id"]) is None
