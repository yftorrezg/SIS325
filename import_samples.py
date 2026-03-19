import asyncio, json, sys
sys.path.insert(0, '/app')
from app.database import engine
from sqlalchemy import text as sa_text

JSONL_PATH = "/tmp/tramites_dataset.jsonl"

async def import_samples():
    samples = []
    with open(JSONL_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                obj = json.loads(line)
                samples.append((obj["text"], obj["label"]))

    print(f"Loaded {len(samples)} samples from JSONL")

    async with engine.begin() as conn:
        inserted = 0
        skipped = 0
        for txt, label in samples:
            r = await conn.execute(
                sa_text("SELECT id FROM training_samples WHERE text = :t LIMIT 1"),
                {"t": txt}
            )
            if r.fetchone():
                skipped += 1
                continue
            await conn.execute(
                sa_text("""
                    INSERT INTO training_samples (id, text, label, verified, source, created_at)
                    VALUES (gen_random_uuid(), :t, :l, true, 'jsonl_import', NOW())
                """),
                {"t": txt, "l": label}
            )
            inserted += 1

    print(f"Done: {inserted} inserted, {skipped} skipped (duplicates)")

asyncio.run(import_samples())
