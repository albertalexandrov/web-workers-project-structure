from pydantic_i18n import PydanticI18n

FIELD_REQUIRED = "Обязательное поле"

translations = {
    "ru_RU": {
        "Field required": FIELD_REQUIRED,
        "Input should be a valid integer, unable to parse string as an integer": "Значение должно быть целым числом",
        "Input should be '{}' or '{}'": "Ожидается значение '{}' или '{}'",
        "Input should be a valid URL, relative URL without a base": "Некорректная ссылка"
    }
}

locale = PydanticI18n(translations, "ru_RU")
