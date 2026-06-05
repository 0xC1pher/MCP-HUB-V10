export const jsonResponse = (data) => ({
    output: JSON.stringify(data, null, 2),
    metadata: data
});
