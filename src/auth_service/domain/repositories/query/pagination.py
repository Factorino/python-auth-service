from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Pagination:
    page: int = 1
    page_size: int = 25

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size
