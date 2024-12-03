import React, { ReactElement, useEffect, useRef } from 'react';
import { CKEditor } from '@ckeditor/ckeditor5-react';
import editor from '../../ckeditor5/build/ckeditor';

function MyCKEditor(props: any): ReactElement | null {
    const classicEditor: any = editor;
    const editorConfiguration = { extraPlugins: [MyCustomUploadAdapterPlugin] };

    function MyCustomUploadAdapterPlugin(editor) {
        editor.plugins.get('FileRepository').createUploadAdapter = loader => {
            loader.upload_path = props.upload_path;
            return new MyUploadAdapter(loader);
        };
    }

    return (
        <div>
            <CKEditor editor={classicEditor} data={props.initialData} config={editorConfiguration} onChange={props.onChange} />
        </div>
    );
}

export default MyCKEditor;
class MyUploadAdapter {
    private loader: any;
    private url: any;
    private xhr: any;

    constructor(props: any) {
        this.loader = props;
        this.url = `/be/aws/upload`;
    }

    // Starts the upload process.
    upload() {
        return new Promise((resolve, reject) => {
            this._initRequest();
            this._initListeners(resolve, reject);
            this._sendRequest();
        });
    }

    // Aborts the upload process.
    abort() {
        if (this.xhr) {
            this.xhr.abort();
        }
    }

    // Example implementation using XMLHttpRequest.
    _initRequest() {
        const xhr = (this.xhr = new XMLHttpRequest());
        xhr.open('POST', this.url, true);
        xhr.responseType = 'json';
        xhr.setRequestHeader('Access-Control-Allow-Origin', '*');
        // xhr.setRequestHeader('Content-Type', 'multipart/form-data');
    }

    // Initializes XMLHttpRequest listeners.
    _initListeners(resolve, reject) {
        const xhr = this.xhr;
        const loader = this.loader;
        const genericErrorText = "Couldn't upload file:" + ` ${loader.file.name}.`;

        xhr.addEventListener('error', () => reject(genericErrorText));
        xhr.addEventListener('abort', () => reject());
        xhr.addEventListener('load', () => {
            const response = xhr.response;
            if (!response || response.error) {
                return reject(response && response.error ? response.error.message : genericErrorText);
            }

            // If the upload is successful, resolve the upload promise with an object containing
            // at least the "default" URL, pointing to the image on the server.
            resolve({
                default: response.s3_url,
            });
        });

        if (xhr.upload) {
            xhr.upload.addEventListener('progress', evt => {
                if (evt.lengthComputable) {
                    loader.uploadTotal = evt.total;
                    loader.uploaded = evt.loaded;
                }
            });
        }
    }

    // Prepares the data and sends the request.
    _sendRequest() {
        const formData = new FormData();
        this.loader.file.then(result => {
            formData.append('file_object', result);
            formData.append('upload_path', this.loader.upload_path);
            this.xhr.send(formData);
        });
    }
}
