const Product = require("../models/Product");

class ProductRepository {
  create(data) {
    return Product.create(data);
  }

  findById(id) {
    return Product.findById(id);
  }

  findPaginated({ page = 1, limit = 10, filters = {} }) {
    const skip = (page - 1) * limit;

    return Product.find(filters)
      .skip(skip)
      .limit(limit)
      .sort({ createdAt: -1 });
  }

  update(id, data) {
    return Product.findByIdAndUpdate(id, data, { new: true });
  }

  softDelete(id) {
    return Product.findByIdAndUpdate(
      id,
      { deletedAt: new Date() },
      { new: true }
    );
  }
}

module.exports = new ProductRepository();
