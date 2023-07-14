from httpx import AsyncClient

global auth_token


async def test_create_user(ac: AsyncClient):
    response = await ac.post("/auth/create_user", json={
              "email": "test@mail.ru",
              "username": "admin",
              "password": "Admin1$3adsfas",
              "confirmed_password": "Admin1$3adsfas",
              "phone": "+79001002343"
            })

    assert response.status_code == 201
    assert response.json()["message"] == 'Successfully created user ' \
                                         'Email(test@mail.ru) ' \
                                         'Username(admin)'


async def test_login_and_get_info_user(ac: AsyncClient):
    global auth_token
    response = await ac.post("/auth/login", data={
        "grant_type": "password",
        "username": "admin",
        "password": "Admin1$3adsfas"
    })
    assert response.status_code == 200
    assert response.json()["token_type"] == 'Bearer'

    auth_token = f'{response.json()["token_type"]} {response.json()["access_token"]}'

    response = await ac.get("/auth/my_user", headers={'Authorization': auth_token})
    assert response.status_code == 200
    assert response.json()["email"] == 'test@mail.ru'
    assert response.json()["username"] == 'admin'
    assert response.json()["phone"] == '+79001002343'
    assert response.json()["is_active"] is True
    assert response.json()["is_verified"] is False


async def test_update_user(ac: AsyncClient):
    response = await ac.put("/auth/update_user/", headers={'Authorization': auth_token},
                            json={"username": "admin1"})
    assert response.status_code == 200


async def test_get_user_info_by_username(ac: AsyncClient):
    response = await ac.get("/auth/admin1/", headers={'Authorization': auth_token})
    assert response.status_code == 200
    assert response.json()["username"] == 'admin1'


async def test_reset_password(ac: AsyncClient):
    response = await ac.post("/auth/reset_password/", json={
        "email": "test@mail.ru"
    })
    assert response.status_code == 200

# требуется всегда новый токен из письма
# async def test_change_password(ac: AsyncClient):
#     response = await ac.post("/auth/change_password/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2V"
#                              "ybmFtZSI6ImFkbWluMSIsInR5cGUiOiJyZXNldF9wYXNzd29yZCIsImV4cCI6"
#                              "MTY4OTMzODQwN30.RJ25OEymvu8-2cPis9Eqjt9wlRmfSUj-UGzGO6xrG7M",
#                              headers={'Authorization': auth_token},
#                              json={"new_password": "Stygf11134&43", "confirmed_password": "Stygf11134&43"})
#     assert response.status_code == 200


# async def test_change_old_password(ac: AsyncClient):
#     response = await ac.post("/auth/change_old_password",
#                              headers={'Authorization': auth_token},
#                              json={"new_password": "UYGYUGdsdf&43", "old_password": "Stygf11134&43"})
#     assert response.status_code == 200
#     assert response.json()["message"] == 'Password by username (admin1) successfully updated.'
