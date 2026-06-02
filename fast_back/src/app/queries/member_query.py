from sqlalchemy import text

# 이메일 중복확인
EXISTS_MEMBER_QUERY = text("""
    SELECT COUNT(*)
    FROM TBL_MEMBER
    WHERE MEMBER_EMAIL = :member_email
        AND MEMBER_PROVIDER = :member_provider
""")

CREATE_MEMBER_QUERY = text("""
    INSERT INTO TBL_MEMBER (
        ID, MEMBER_EMAIL, MEMBER_PASSWORD, MEMBER_NAME, MEMBER_PICTURE,
        MEMBER_AGE, MEMBER_PROVIDER, MEMBER_CREATED_AT                        
    )
    VALUES (
        SEQ_MEMBER.NEXTVAL, :member_email, :member_password, :member_name, :member_picture,
        :member_age, :member_provider, SYSDATE
    )
""")

# 회원 조회(id)
FIND_MEMBER_BY_ID_QUERY = text("""
    SELECT
        ID, MEMBER_EMAIL, MEMBER_PASSWORD, MEMBER_NAME, MEMBER_PICTURE,
        MEMBER_AGE, MEMBER_PROVIDER_ID, MEMBER_PROVIDER, MEMBER_CREATED_AT 
    FROM TBL_MEMBER
    WHERE ID = :id
""")

# 회원 조회(member_email, member_provider)
FIND_MEMBER_BY_EMAIL_AND_PROVIDER_QUERY = text("""
    SELECT
        ID, MEMBER_EMAIL, MEMBER_PASSWORD, MEMBER_NAME, MEMBER_PICTURE,
        MEMBER_AGE, MEMBER_PROVIDER_ID, MEMBER_PROVIDER, MEMBER_CREATED_AT 
    FROM TBL_MEMBER
    WHERE MEMBER_EMAIL = :member_email
        AND MEMBER_PROVIDER = :member_provider
""")

# 회원 전체 조회
FIND_MEMBERS_QUERY = text("""
    SELECT
        ID, MEMBER_EMAIL, MEMBER_PASSWORD, MEMBER_NAME, MEMBER_PICTURE,
        MEMBER_AGE, MEMBER_PROVIDER_ID, MEMBER_PROVIDER, MEMBER_CREATED_AT 
    FROM TBL_MEMBER 
""")

# 회원 정보 수정
UPDATE_MEMBER_QUERY = text("""
    UPDATE TBL_MEMBER
    SET 
        MEMBER_PASSWORD = :member_password,
        MEMBER_NAME = :member_name,
        MEMBER_AGE = :member_age
    WHERE ID = :id
""")

# 회원 삭제
DELETE_MEMBER_QUERY = text("""
    DELETE FROM TBL_MEMBER
    WHERE ID = :id
""")
