import typing as T
import asyncio

from .interfaces import ICodeGenerator, IUOW

from src.core.config import ENVS


class CodeBatchGenerator:
    def __init__(self, uow: IUOW, code_generator: ICodeGenerator) -> None:
        self.uow = uow
        self.code_generator = code_generator

    def _generate_batch(self, target: int) -> set[str]:
        codes: T.Set[str] = set()
        attempts = 0

        while (len(codes) < target) and (attempts < target * 3):
            generated_code = self.code_generator.generate_code()
            codes.add(generated_code)

            attempts += 1

        if len(codes) < target:
            raise RuntimeError(
                f"Could only generate {len(codes)}/{target} unique codes"
            )

        return codes

    async def refill_code_storage(
        self,
        target_unused: int = ENVS.CODE_GENERATOR.TARGET_UNUSED_STORED_CODES,
        batch_size: int = ENVS.CODE_GENERATOR.BATCH_SIZE,
    ) -> None:
        async with self.uow as uow:
            unused_db_codes = await uow.codes.count_unused()

            if unused_db_codes >= target_unused:
                # I don't want to store a huge amount of code
                return

            needed = target_unused - unused_db_codes
            inserted_total = 0

            while inserted_total < needed:
                batch_to_generate = min(batch_size, needed - inserted_total)
                new_codes = self._generate_batch(batch_to_generate)

                inserted_counts = await uow.codes.bulk_insert_unused(new_codes)

                inserted_total += inserted_counts

                # Small delay for preventing DB from overwhelming
                await asyncio.sleep(1)
