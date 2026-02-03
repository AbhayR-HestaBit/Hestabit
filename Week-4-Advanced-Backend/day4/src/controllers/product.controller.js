const ProductService = require("../services/product.service");

exports.getProducts = async (req, res, next) => {
  try {
    const products = await ProductService.list(req.query);
    res.json({ success: true, data: products });
  } catch (err) {
    next(err);
  }
};

exports.deleteProduct = async (req, res, next) => {
  try {
    await ProductService.softDelete(req.params.id);
    res.json({ success: true });
  } catch (err) {
    next(err);
  }
};
