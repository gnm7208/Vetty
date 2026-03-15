"""Review schemas."""

from __future__ import annotations

from marshmallow import Schema, ValidationError, fields, validates_schema


class ReviewSchema(Schema):
    id = fields.Int(dump_only=True)
    rating = fields.Int(required=True)
    comment = fields.Str(allow_none=True)
    product_id = fields.Int(allow_none=True)
    service_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ReviewWriteSchema(Schema):
    rating = fields.Int(required=True)
    comment = fields.Str(allow_none=True)
    product_id = fields.Int(allow_none=True)
    service_id = fields.Int(allow_none=True)

    @validates_schema
    def validate_rating_and_subject(self, data, **kwargs):
        rating = data.get("rating")
        if rating is None or rating < 1 or rating > 5:
            raise ValidationError("Rating must be between 1 and 5", field_name="rating")

        product_id = data.get("product_id")
        service_id = data.get("service_id")
        if bool(product_id) == bool(service_id):
            raise ValidationError(
                "Provide either product_id or service_id, but not both",
                field_name="product_id",
            )

        comment = data.get("comment")
        if comment and len(comment) > 500:
            raise ValidationError("Comment cannot exceed 500 characters", field_name="comment")
