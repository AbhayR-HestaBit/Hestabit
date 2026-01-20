/*export function groupBy(arr, key) {
  return arr.reduce((acc, item) => {
    const k = item[key];
    acc[k] = acc[k] || [];
    acc[k].push(item);
    return acc;
  }, {});
}*/
export function groupBy(arr, key) {
return arr.reduce((acc, item) => {
const group = item[key]
if (!acc[group]) acc[group] = []
acc[group].push(item)
return acc
}, {})
}


