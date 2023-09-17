export default {
  template: "<div></div>",
  mounted() {
    const container = this.$el;

    // Loading PDF.js and the viewer
    const pdfLinkService = new pdfjsViewer.PDFLinkService();
    const pdfViewer = new pdfjsViewer.PDFViewer({
      container: container,
      linkService: pdfLinkService,
    });
    pdfLinkService.setViewer(pdfViewer);

    // Store the pdfViewer instance for other methods
    this.pdfViewer = pdfViewer;
  },
  methods: {
    load_pdf(pdf_url) {
      // Loading the PDF document
      const loadingTask = window.pdfjsLib.getDocument(pdf_url);
      loadingTask.promise.then((pdfDocument) => {
        this.pdfViewer.setDocument(pdfDocument);
      });
    },
    set_page(page_number) {
      this.pdfViewer.currentPageNumber = page_number;
    },
  },
};
