from httpx import AsyncClient

global auth_token


async def test_login_and_get_token(ac: AsyncClient):
    global auth_token
    response = await ac.post("/auth/create_user", json={
        "email": "test12@mail.ru",
        "username": "admin2",
        "password": "Admin1$3adsfas",
        "confirmed_password": "Admin1$3adsfas",
        "phone": "+79001002344"
    })

    assert response.status_code == 201
    assert response.json()["message"] == 'Successfully created user ' \
                                         'Email(test12@mail.ru) ' \
                                         'Username(admin2)'

    response = await ac.post("/auth/login", data={
        "grant_type": "password",
        "username": "admin2",
        "password": "Admin1$3adsfas"
    })
    assert response.status_code == 200
    assert response.json()["token_type"] == 'Bearer'

    auth_token = f'{response.json()["token_type"]} {response.json()["access_token"]}'


async def test_create_group(ac: AsyncClient):
    response = await ac.post("/crypt/create_group", headers={'Authorization': auth_token},
                             json={"name": "test_group"})
    assert response.status_code == 201
    assert response.json()["message"] == 'Successfully created group (test_group)' \
                                         ' for User admin2'


async def test_get_group_update_delete(ac: AsyncClient):
    response = await ac.get("/crypt/get_all_my_groups", headers={'Authorization': auth_token})
    assert response.status_code == 200
    assert response.json()[0].get('name') == 'test_group'
    group_id = response.json()[0].get('id')

    response = await ac.put("/crypt/update_group", headers={'Authorization': auth_token},
                            json={"id": group_id, "name": "update_group"})
    assert response.status_code == 200
    assert "Successfully update group" in response.json()["message"]

    response = await ac.delete("/crypt/delete_group",
                               headers={'Authorization': auth_token},
                               params={'group_id': group_id})
    assert response.status_code == 200

    response = await ac.get("/crypt/get_all_my_groups", headers={'Authorization': auth_token})
    assert response.status_code == 200
    assert len(response.json()) == 0


async def test_create_auth_data(ac: AsyncClient):
    response = await ac.post("/crypt/create_group", headers={'Authorization': auth_token},
                             json={"name": "new_group"})
    assert response.status_code == 201
    assert response.json()["message"] == 'Successfully created group (new_group)' \
                                         ' for User admin2'

    response = await ac.get("/crypt/get_all_my_groups", headers={'Authorization': auth_token})
    assert response.status_code == 200
    assert response.json()[0].get('name') == 'new_group'
    group_id = response.json()[0].get('id')
    for service_name, login in [('github', 'test1'), ('vk', 'test2'),
                                ('inst', 'test3')]:
        response = await ac.post("/crypt/create_auth_data",
                                 headers={'Authorization': auth_token},
                                 json={'service_name': service_name,
                                       'login': login,
                                       'password': 'password', 'group_id': group_id})
        assert response.status_code == 201


async def test_get_auth_data_by_group_update_delete(ac: AsyncClient):
    response = await ac.get("/crypt/get_all_my_groups", headers={'Authorization': auth_token})
    assert response.status_code == 200
    assert response.json()[0].get('name') == 'new_group'
    group_id = response.json()[0].get('id')

    response = await ac.get("/crypt/get_all_auth_data_by_group",
                            headers={'Authorization': auth_token},
                            params={'group_id': group_id})
    assert response.status_code == 200
    assert len(response.json()) == 3

    auth_data_id = [auth_data.get('id') for auth_data in response.json() if auth_data.get('service_name') == 'github']
    assert len(auth_data_id) == 1

    response = await ac.put("/crypt/update_auth_data",
                            headers={'Authorization': auth_token},
                            json={'id': auth_data_id[0], 'service_name': 'github_new'})
    assert response.status_code == 200

    response = await ac.get("/crypt/get_all_auth_data_by_group",
                            headers={'Authorization': auth_token},
                            params={'group_id': group_id})
    assert response.status_code == 200
    auth_data_id = [auth_data.get('id') for auth_data in response.json()
                    if auth_data.get('service_name') == 'github_new']
    assert len(auth_data_id) == 1

    response = await ac.delete("/crypt/delete_auth_data",
                               headers={'Authorization': auth_token},
                               params={'auth_data_id': auth_data_id[0]})
    assert response.status_code == 200

    response = await ac.get("/crypt/get_all_auth_data_by_group",
                            headers={'Authorization': auth_token},
                            params={'group_id': group_id})
    assert response.status_code == 200
    auth_data_id = [auth_data.get('id') for auth_data in response.json()
                    if auth_data.get('service_name') == 'github_new']
    assert len(auth_data_id) == 0


async def test_get_data_groups(ac: AsyncClient):
    response = await ac.get("/crypt/get_data_groups", headers={'Authorization': auth_token})
    assert response.status_code == 200
    assert len(response.json()) == 2 and response.json()[0].get('group_name') == 'new_group'


async def test_get_decrypt_password(ac: AsyncClient):
    response = await ac.get("/crypt/get_data_groups", headers={'Authorization': auth_token})
    assert response.status_code == 200
    auth_data_id = response.json()[0].get('auth_data_id')

    response = await ac.get("/crypt/decrypt_password", headers={'Authorization': auth_token},
                            params={'auth_data_id': auth_data_id})
    assert response.status_code == 200
    assert response.json().get('decrypt_password') == 'password'


async def test_search_auth_data(ac: AsyncClient):
    response = await ac.post("/crypt/search_auth_data", headers={'Authorization': auth_token},
                             json={'service_name': 'inst'})
    assert response.status_code == 200
    answer = response.json()
    assert len(answer) == 1 and answer[0].get('service_name') == 'inst' \
           and answer[0].get('login') == 'test3' and answer[0].get('group_name') == 'new_group'


async def test_generate_password_endpoint(ac: AsyncClient):
    response = await ac.get("/crypt/generate_password")
    assert response.status_code == 200
    assert len(response.json().get('generated_password')) == 12
