# Тестовое задание: Система конвертации документов в сериях

## Описание задачи
Реализовать систему, которая позволяет:
1. Создавать серии документов
2. Загружать PDF файлы в серии
3. Конвертировать PDF в DOC через EC2 инстансы

## Технический стек
- AWS (EC2, Lambda, S3, SQS)
- REST API
- База данных на выбор

## Основной функционал

### 1. Работа с сериями
- Создание серии (название = ID серии)
- Загрузка PDF в серию
- Просмотр списка документов в серии

### 2. Конвертация документов
- При загрузке PDF, документ попадает в очередь на конвертацию
- Конвертация выполняется на EC2 инстансах
- Lambda управляет запуском/остановкой EC2:
  * Запускает инстанс при появлении документов в очереди
  * Останавливает при пустой очереди
  * Максимум 2 работающих инстанса одновременно

## Требования к реализации

### API endpoints
```
POST /api/series
GET /api/series
POST /api/series/{id}/documents
GET /api/series/{id}/documents
```

### Lambda функция
```python
def manage_conversion_instances(event, context):
    # Управление EC2 инстансами для конвертации
    # - Мониторинг очереди
    # - Запуск/остановка EC2
    # - Контроль количества инстансов
```

### EC2 инстанс
- Простой воркер, который:
  * Берет документ из очереди
  * Конвертирует PDF в DOC (любой конвертер)
  * Сохраняет результат в S3

## Ограничения
- Максимум 2 активных EC2 инстанса
- Поддерживаются только PDF файлы до 10MB
- Название серии: только латинские буквы, цифры и дефис

## Что предоставляется
- Доступ к тестовому AWS аккаунту
- Базовый AMI для EC2

## Ожидаемые результаты
1. Исходный код в git
2. Инструкция по развертыванию
3. Примеры использования API
4. Краткое описание решения

## Срок выполнения
5 часов
