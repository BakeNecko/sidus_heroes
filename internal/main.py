from internal.app.app import create_app

app = create_app()


@app.on_event("startup")
async def on_startup():
    # TODO: не критичный баг из-за threding миграций
    # <duplicate key value violates unique constraint "pg_type_typname_nsp_index">
    await app.container.db().init_db()
    await app.container.cache().ping()


@app.get("/")
def main():
    return {"status": "ok"}
