const ProductRepository = require("../repositories/product.repository");

class ProductService {
  async list(query) {
    const {
      search,
      minPrice,
      maxPrice,
      status,
      tags,
      sort = "createdAt:desc",
      page = 1,
      limit = 10,
      includeDeleted = false
    } = query;

    const filter = {};

    if (!includeDeleted) {
      filter.deletedAt = null;
    }

    if (status) {
      filter.status = status;
    }

    if (minPrice || maxPrice) {
      filter.price = {};
      if (minPrice) filter.price.$gte = Number(minPrice);
      if (maxPrice) filter.price.$lte = Number(maxPrice);
    }

    if (tags) {
      filter.tags = { $in: tags.split(",") };
    }

    if (search) {
      filter.name = { $regex: search, $options: "i" };
    }

    const [sortField, sortOrder] = sort.split(":");
    const sortObj = { [sortField]: sortOrder === "asc" ? 1 : -1 };

    const skip = (Number(page) - 1) * Number(limit);

    return ProductRepository.find(filter, {
      sort: sortObj,
      skip,
      limit: Number(limit)
    });
  }

  async softDelete(id) {
    return ProductRepository.update(id, {
      deletedAt: new Date()
    });
  }
}

module.exports = new ProductService();
