export default {
  // outer div is container - inner div is viewer
  template: "<div class='pdfViewerContainer'><div></div></div>",
  mounted() {
	// my container
    const container = this.$el;
    
    // check the library is available
    if (!pdfjsLib.getDocument || !pdfjsViewer.PDFViewer) {
	}

	const eventBus = new pdfjsViewer.EventBus();

    // Loading PDF.js and the viewer
    // (Optionally) enable hyperlinks within PDF files.
	const pdfLinkService = new pdfjsViewer.PDFLinkService({
	  eventBus,
	});
    const pdfViewer = new pdfjsViewer.PDFViewer({
      container,
      eventBus,
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
      loadingTask.promise.then(
		(pdfDocument) => {
        this.pdfViewer.setDocument(pdfDocument);
      	},
      	 // Error function
        (exception) => {
			console.error(exception);
		}
      );
    },
    set_page(page_number) {
      this.pdfViewer.currentPageNumber = page_number;
    },
  },
};
