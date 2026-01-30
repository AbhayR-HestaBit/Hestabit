const User = require("../models/User");

class UserRepository {
  create(data) {
    return User.create(data);
  }

  findById(id) {
    return User.findById(id);
  }

  findPaginated({ page = 1, limit = 10 }) {
    const skip = (page - 1) * limit;

    return User.find()
      .skip(skip)
      .limit(limit)
      .sort({ createdAt: -1 });
  }

  update(id, data) {
    return User.findByIdAndUpdate(id, data, { new: true });
  }

  delete(id) {
    return User.findByIdAndDelete(id);
  }
}

module.exports = new UserRepository();
