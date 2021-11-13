function searchPhoto() {

  var apigClient = apigClientFactory.newClient({
    apiKey: "WnqHXLguUU3sf7qGMjmOLaRCD3gmg89J7VyE8qvG"
  });

  var user_message = document.getElementById('note-textarea').value;

  var body = {};
  var params = { q: user_message };
  var additionalParams = {
    headers: {
      'Content-Type': "application/json"
    }
  };

  apigClient.searchGet(params, body, additionalParams).then(function (res) {
    document.getElementById("gallery_showcase").innerHTML = ""
    var data = {}
    var data_array = []
    resp_data = res.data.hits.hits
    length_of_response = resp_data.length;
    if (length_of_response == 0) {
      document.getElementById("gallery_showcase").innerHTML = "No images found.."
      document.getElementById("gallery_showcase").style.display = "block";

    }
    console.log(resp_data)

    uploadCenterClone = document.getElementById("upload_center")
    uploadCenter = document.getElementById("upload_center")
    uploadCenter.parentNode.removeChild(uploadCenter)

    resp_data.forEach(function (obj) {

      console.log(obj)
      var imgDiv = document.createElement("div")
      imgDiv.className = "gallery"

      var a = document.createElement("a")
      a.target = "_blank"
      a.href = "https://s3.amazonaws.com/nm3223.voice-photo-album.b2.w6998.ccbd.f2021/" + obj._source.objectKey

      var image = document.createElement("img")
      image.src = a.href
      image.alt = obj._source.objectKey
      image.width = "600"
      image.height = "400"

      a.appendChild(image)

      var description = document.createElement("div")
      description.className = "desc"
      description.innerHTML = obj._source.objectKey + "|" + new Date(obj._source.createdTimestamp).toLocaleDateString("en-US")

      imgDiv.appendChild(a)
      imgDiv.appendChild(description)

      document.getElementById("gallery_showcase").appendChild(imgDiv)
      document.getElementById("gallery_showcase").re

    });

    document.body.appendChild(uploadCenterClone)
  }).catch(function (result) {
    console.log("Here")
    console.error(result)
  });



}

function getBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    // reader.onload = () => resolve(reader.result)
    reader.onload = () => {
      let encoded = reader.result.replace(/^data:(.*;base64,)?/, '');
      if ((encoded.length % 4) > 0) {
        encoded += '='.repeat(4 - (encoded.length % 4));
      }
      resolve(encoded);
    };
    reader.onerror = error => reject(error);
  });
}




function uploadPhoto() {
  var file = document.getElementById('file_path').files[0];
  const reader = new FileReader();

  var encoded_image = getBase64(file).then(
    data => {
      console.log(data)
      var apigClient = apigClientFactory.newClient({
        apiKey: "WnqHXLguUU3sf7qGMjmOLaRCD3gmg89J7VyE8qvG"
      });

      var body = data;
      var params = {
        "x-api-key": "WnqHXLguUU3sf7qGMjmOLaRCD3gmg89J7VyE8qvG",
        "file-name": file.name,
        "Content-Type": file.type + ";base64",
        "bucket": "nm3223.voice-photo-album.b2.w6998.ccbd.f2021",
        "x-amz-meta-customLabels": document.getElementById("uploadText").value
      }
      var additionalParams = {};
      apigClient.uploadPut(params, body, additionalParams).then(function (res) {
        if (res.status == 200) {
          document.getElementById("fileName").innerHTML = "File Upload Complete"
        }
      })
    });

}



function showFile(input) {
  document.getElementById("fileName").innerHTML = "File : " + input.files[0].name
}