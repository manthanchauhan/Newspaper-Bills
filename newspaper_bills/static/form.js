var quill = new Quill('#editor-container', {
    modules: {
        toolbar: [
        [{
        header: [1, 2, false]
        }],
        ['bold', 'italic', 'underline'],
        ['image', 'code-block']
       ]
      },
     placeholder: 'Describe your issue in detail',
     theme: 'snow' // or 'bubble'
     });