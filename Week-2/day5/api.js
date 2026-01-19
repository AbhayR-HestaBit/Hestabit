export async function fetchProducts() {
  try {
    const res = await fetch("https://dummyjson.com/products");
    if (!res.ok) throw new Error("API failed");

    const data = await res.json();
    return data.products;
  } catch (err) {
    console.error(err);
    throw err;
  }
}
