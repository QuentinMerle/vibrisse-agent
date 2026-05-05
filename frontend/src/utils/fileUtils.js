/**
 * Converts a File object to a base64 string (without the data:image/... prefix)
 * @param {File} file 
 * @returns {Promise<string>}
 */
export const processImageFile = (file) => {
  return new Promise((resolve, reject) => {
    if (!file || !file.type.startsWith('image/')) {
      reject(new Error("File is not an image"));
      return;
    }

    const reader = new FileReader();
    reader.onload = (ev) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        const base64 = canvas.toDataURL('image/png').split(',')[1];
        resolve(base64);
      };
      img.onerror = () => reject(new Error("Failed to load image"));
      img.src = ev.target.result;
    };
    reader.onerror = () => reject(new Error("Failed to read file"));
    reader.readAsDataURL(file);
  });
};
