# Reference content and dependencies

Arabic text in `App/Resources/verses.json` is an unmodified excerpt of the Tanzil Uthmani Quran text, verses 1:1–1:7. Source: https://tanzil.net/.

Tanzil grants verbatim copying and distribution with attribution and a link to its site; changing the text is not allowed. Licence notice: https://tanzil.net/docs/text_license. The local preparation file preserves the complete source text separately. Normalization for future recognition must not alter the displayed source content.
The original copyright and usage notice is preserved in `App/Resources/TANZIL-NOTICE.txt` and bundled with the app.

The English excerpt is Marmaduke Pickthall's published translation, retained verbatim from the prepared reference file. The project uses it as a public-domain translation and labels its source in the interface.

Meta Wearables Device Access Toolkit 1.0.1 is downloaded by Swift Package Manager. Its SDK, frameworks and sample code retain Meta's terms and notices: https://github.com/facebook/meta-wearables-dat-ios. No Meta sample source is copied into this first application; the published samples and SDK interfaces informed integration.

The MIT licence covers original Ayah Lens code, not third-party SDKs or reference texts. No recitation recordings or model weights are included in Git; locally assembled development builds bundle the model as described below.

## Local recognition

The installed prototype bundles Meta Omnilingual ASR CTC-300M through aufklarer’s 5-second CoreML INT8 conversion, labelled Apache-2.0 by its publisher:

- Original model: https://github.com/facebookresearch/omnilingual-asr
- CoreML export: https://huggingface.co/aufklarer/Omnilingual-ASR-CTC-300M-CoreML-INT8
- Swift reference studied for waveform normalization, tensor layout and CTC semantics: https://github.com/soniqo/speech-swift/tree/main/Sources/OmnilingualASR

The event implementation supplies its own native inference adapter, Arabic-only decoding restriction, rolling audio windows and Al-Fatihah matcher. The model and conversion predate the event and are not claimed as original work. The preparation helper extracts vocabulary entries without changing their token identifiers; these artifacts and model weights are excluded from Git. No third-party Swift implementation was copied. The Apache 2.0 licence and source notice are bundled as MODEL-NOTICE.txt.

## Muse streaming protocol

Muse Voice Transcribe is accessed through the hosted Meta Model API; its weights are not part of this repository. The original client and PCM adapter follow Meta’s published realtime and voice schemas: https://dev.meta.ai/docs/api-reference/voice/realtime and https://dev.meta.ai/docs/api-reference/voice/schemas. A local synthetic-server probe verifies the wire format without claiming provider transcription accuracy. Muse Spark remains unimplemented.
