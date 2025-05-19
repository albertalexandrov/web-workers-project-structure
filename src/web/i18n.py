from pydantic_i18n import PydanticI18n

FIELD_REQUIRED = "Обязательное поле"

translations = {
    "ru_RU": {
        "Field required": FIELD_REQUIRED,
        "Input should be a valid integer, unable to parse string as an integer": "Значение должно быть целым числом",
        "Input should be '{}' or '{}'": "Ожидается значение '{}' или '{}'",
        "Input should be a valid URL, relative URL without a base": "Некорректная ссылка",
        "Input should be greater than 0": "Значение должно быть целым положительным числом",
        "Input should be a valid UUID, invalid group length in group 4: expected {}, found {}": "Значение должно быть корректным UUID"
    }
}

locale = PydanticI18n(translations, "ru_RU")
