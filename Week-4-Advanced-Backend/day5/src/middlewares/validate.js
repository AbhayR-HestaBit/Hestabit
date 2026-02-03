const Joi = require('joi');


const createProductSchema = Joi.object({
  name: Joi.string().trim().min(3).max(100).required(),
  price: Joi.number().positive().required(),
  description: Joi.string().max(500).optional(),
  category: Joi.string().optional(),
  tags: Joi.array().items(Joi.string()).optional(),
  stock: Joi.number().integer().min(0).optional()
});

const updateProductSchema = Joi.object({
  name: Joi.string().trim().min(3).max(100).optional(),
  price: Joi.number().positive().required(),
  description: Joi.string().max(500).optional(),
  category: Joi.string().optional(),
  tags: Joi.array().items(Joi.string()).optional(),
  stock: Joi.number().integer().min(0).optional()
}).min(1);

const validate = (schema) => {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.body, {
      abortEarly: false,
      stripUnknown: true
    });

    if (error) {
      const errors = error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message
      }));
      
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors
      });
    }

    req.body = value;
    next();
  };
};

module.exports = {
  validate,
  createProductSchema,
  updateProductSchema
};