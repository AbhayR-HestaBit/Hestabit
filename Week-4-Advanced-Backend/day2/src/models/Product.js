const mongoose = require("mongoose");

const ProductSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
      index: true
    },
    price: {
      type: Number,
      required: true
    },
    status: {
      type: String,
      enum: ["active", "inactive"],
      default: "active",
  index: true
    },
    tags: {
      type: [String],
      index: true
    }
  },
  { timestamps: true }
);
ProductSchema.index({ status: 1, createdAt: -1 });

ProductSchema.virtual("displayPrice").get(function () {
  return `₹${this.price}`;
});

ProductSchema.set("toJSON", { virtuals: true });
ProductSchema.set("toObject", { virtuals: true });


module.exports = mongoose.model("Product", ProductSchema);
