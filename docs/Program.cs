using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using DW = DocumentFormat.OpenXml.Drawing.Wordprocessing;
using A = DocumentFormat.OpenXml.Drawing;
using PIC = DocumentFormat.OpenXml.Drawing.Pictures;

string outputFile = args.Length > 0 ? args[0] : "/mnt/agents/output/FAIR-Freight-Agentic-Investigation/docs/F.AIR._Project_Report.docx";
using var doc = WordprocessingDocument.Create(outputFile, WordprocessingDocumentType.Document);
var mainPart = doc.AddMainDocumentPart();
mainPart.Document = new Document(new Body());
var body = mainPart.Document.Body!;

AddStyles(mainPart);
AddNumbering(mainPart);

var coverBgId = AddImage(mainPart, "/mnt/agents/output/FAIR-Freight-Agentic-Investigation/docs/cover_bg.png");
uint prId = 1;

// Cover
AddCoverSection(body, coverBgId, ref prId);

// TOC
AddTocSection(body);

// Content with header/footer
AddContentSection(doc, body, mainPart, ref prId);

SetUpdateFieldsOnOpen(mainPart);
doc.Save();
Console.WriteLine($"Document saved to: {outputFile}");

// ========================================================================
// Styles
// ========================================================================
void AddStyles(MainDocumentPart mainPart)
{
    var sp = mainPart.AddNewPart<StyleDefinitionsPart>();
    sp.Styles = new Styles();

    sp.Styles.Append(new Style(
        new StyleName { Val = "Normal" },
        new StyleParagraphProperties(
            new SpacingBetweenLines { After = "200", Line = "312", LineRule = LineSpacingRuleValues.Auto }),
        new StyleRunProperties(
            new RunFonts { Ascii = "Calibri", HighAnsi = "Calibri", EastAsia = "Microsoft YaHei" },
            new FontSize { Val = "22" },
            new Color { Val = "1f2937" })
    ) { Type = StyleValues.Paragraph, StyleId = "Normal", Default = true });

    sp.Styles.Append(CreateHeadingStyle("Heading1", "heading 1", 0, "36", "1a2744", "600", "240"));
    sp.Styles.Append(CreateHeadingStyle("Heading2", "heading 2", 1, "28", "2d3a35", "400", "160"));
    sp.Styles.Append(CreateHeadingStyle("Heading3", "heading 3", 2, "24", "5a6b62", "280", "120"));

    sp.Styles.Append(new Style(
        new StyleName { Val = "Caption" }, new BasedOn { Val = "Normal" },
        new StyleParagraphProperties(
            new Justification { Val = JustificationValues.Center },
            new SpacingBetweenLines { Before = "60", After = "320" }),
        new StyleRunProperties(new Color { Val = "8a9a90" }, new FontSize { Val = "20" })
    ) { Type = StyleValues.Paragraph, StyleId = "Caption" });

    sp.Styles.Append(CreateTocStyle("TOC1", "toc 1", true, "0", "200"));
    sp.Styles.Append(CreateTocStyle("TOC2", "toc 2", false, "360", "60"));
}

Style CreateHeadingStyle(string id, string name, int level, string fontSize, string color, string spaceBefore, string spaceAfter)
{
    return new Style(
        new StyleName { Val = name }, new BasedOn { Val = "Normal" },
        new StyleParagraphProperties(
            new KeepNext(), new KeepLines(),
            new SpacingBetweenLines { Before = spaceBefore, After = spaceAfter },
            new OutlineLevel { Val = level }),
        new StyleRunProperties(
            new Bold(), new FontSize { Val = fontSize },
            new RunFonts { Ascii = "Calibri", HighAnsi = "Calibri", EastAsia = "Microsoft YaHei" },
            new Color { Val = color })
    ) { Type = StyleValues.Paragraph, StyleId = id };
}

Style CreateTocStyle(string id, string name, bool bold, string indent, string before)
{
    var rpr = new StyleRunProperties(new Color { Val = bold ? "1f2937" : "5a6b62" });
    if (bold) rpr.Append(new Bold());
    return new Style(
        new StyleName { Val = name }, new BasedOn { Val = "Normal" },
        new StyleParagraphProperties(
            new Tabs(new TabStop { Val = TabStopValues.Right, Leader = TabStopLeaderCharValues.Dot, Position = 9350 }),
            new SpacingBetweenLines { Before = before, After = "60" },
            new Indentation { Left = indent }),
        rpr
    ) { Type = StyleValues.Paragraph, StyleId = id };
}

// ========================================================================
// Cover
// ========================================================================
void AddCoverSection(Body body, string coverBgId, ref uint prId)
{
    body.Append(new Paragraph(new Run(CreateFloatingBackground(coverBgId, prId++, "CoverBg"))));
    body.Append(new Paragraph(new ParagraphProperties(new SpacingBetweenLines { Before = "5000" }), new Run()));

    body.Append(new Paragraph(
        new ParagraphProperties(
            new Justification { Val = JustificationValues.Left },
            new Indentation { Left = "1200", Right = "1200" },
            new SpacingBetweenLines { After = "200" }),
        new Run(new RunProperties(
                new FontSize { Val = "96" },
                new Color { Val = "ffffff" },
                new Spacing { Val = 40 }),
            new Text("F.A.I.R."))));

    body.Append(new Paragraph(
        new ParagraphProperties(
            new Justification { Val = JustificationValues.Left },
            new Indentation { Left = "1200", Right = "1200" },
            new SpacingBetweenLines { After = "400" }),
        new Run(new RunProperties(
                new FontSize { Val = "32" },
                new Color { Val = "fd7e14" },
                new Spacing { Val = 30 }),
            new Text("Freight Agentic Investigation & Resolution"))));

    body.Append(new Paragraph(
        new ParagraphProperties(
            new Justification { Val = JustificationValues.Left },
            new Indentation { Left = "1200", Right = "1200" },
            new SpacingBetweenLines { After = "3000" }),
        new Run(new RunProperties(
                new FontSize { Val = "24" },
                new Color { Val = "a0aec0" },
                new Spacing { Val = 20 }),
            new Text("Agentic AI CA-3 Academic Project Report"))));

    body.Append(new Paragraph(
        new ParagraphProperties(new Indentation { Left = "1200" }),
        new Run(new RunProperties(new FontSize { Val = "20" }, new Color { Val = "a0aec0" }),
            new Text("Gatik Johar  |  Harman Singh  |  October 2026"))));

    body.Append(new Paragraph(new ParagraphProperties(new SectionProperties(
        new TitlePage(),
        new SectionType { Val = SectionMarkValues.NextPage },
        new PageSize { Width = 11906, Height = 16838 },
        new PageMargin { Top = 0, Right = 0, Bottom = 0, Left = 0, Header = 0, Footer = 0 }))));
}

// ========================================================================
// TOC
// ========================================================================
void AddTocSection(Body body)
{
    body.Append(CreateHeading1("Table of Contents", "_Toc000"));

    body.Append(new Paragraph(
        new Run(new FieldChar { FieldCharType = FieldCharValues.Begin }),
        new Run(new FieldCode(" TOC \\o \"1-3\" \\h \\z \\u ") { Space = SpaceProcessingModeValues.Preserve }),
        new Run(new FieldChar { FieldCharType = FieldCharValues.Separate })));

    string[,] toc = {
        { "Executive Summary", "1", "3" },
        { "Introduction", "1", "4" },
        { "Proposed Solution", "1", "5" },
        { "System Architecture", "1", "6" },
        { "Agent Design", "1", "7" },
        { "Implementation", "1", "9" },
        { "Evaluation & Testing", "1", "11" },
        { "Limitations & Future Scope", "1", "13" },
        { "Conclusion", "1", "14" },
    };
    for (int i = 0; i < toc.GetLength(0); i++)
        body.Append(new Paragraph(
            new ParagraphProperties(new ParagraphStyleId { Val = $"TOC{toc[i, 1]}" }),
            new Run(new Text(toc[i, 0])), new Run(new TabChar()), new Run(new Text(toc[i, 2]))));

    body.Append(new Paragraph(new Run(new FieldChar { FieldCharType = FieldCharValues.End })));

    body.Append(new Paragraph(new ParagraphProperties(new SectionProperties(
        new SectionType { Val = SectionMarkValues.NextPage },
        new PageSize { Width = 11906, Height = 16838 },
        new PageMargin { Top = 1800, Right = 1440, Bottom = 1440, Left = 1440, Header = 720, Footer = 720 }))));
}

// ========================================================================
// Content
// ========================================================================
void AddContentSection(WordprocessingDocument doc, Body body, MainDocumentPart mainPart, ref uint prId)
{
    var headerPart = mainPart.AddNewPart<HeaderPart>();
    var headerId = mainPart.GetIdOfPart(headerPart);
    headerPart.Header = new Header(new Paragraph(
        new ParagraphProperties(new Justification { Val = JustificationValues.Right }),
        new Run(new RunProperties(new FontSize { Val = "18" }, new Color { Val = "8a9a90" }),
            new Text("F.A.I.R. - Project Report"))));

    var footerPart = mainPart.AddNewPart<FooterPart>();
    var footerId = mainPart.GetIdOfPart(footerPart);
    var fp = new Paragraph(new ParagraphProperties(new Justification { Val = JustificationValues.Center }));
    fp.Append(new Run(new RunProperties(new FontSize { Val = "18" }, new Color { Val = "8a9a90" }),
        new FieldChar { FieldCharType = FieldCharValues.Begin }));
    fp.Append(new Run(new RunProperties(new FontSize { Val = "18" }, new Color { Val = "8a9a90" }),
        new FieldCode(" PAGE ") { Space = SpaceProcessingModeValues.Preserve }));
    fp.Append(new Run(new RunProperties(new FontSize { Val = "18" }, new Color { Val = "8a9a90" }),
        new FieldChar { FieldCharType = FieldCharValues.Separate }));
    fp.Append(new Run(new RunProperties(new FontSize { Val = "18" }, new Color { Val = "8a9a90" }),
        new Text("1")));
    fp.Append(new Run(new RunProperties(new FontSize { Val = "18" }, new Color { Val = "8a9a90" }),
        new FieldChar { FieldCharType = FieldCharValues.End }));
    footerPart.Footer = new Footer(fp);

    // Executive Summary
    body.Append(CreateHeading1("Executive Summary", "_Toc001"));
    body.Append(CreateParagraph("F.A.I.R. (Freight Agentic Investigation & Resolution) is an autonomous multi-agent proof-of-concept designed to investigate and resolve freight exceptions through a structured five-agent workflow. The system demonstrates core agentic AI principles including task planning, multi-step execution, decision-making under uncertainty, adversarial validation, and human-in-the-loop governance."));
    body.Append(CreateParagraph("Freight exceptions, including damage, delay, customs hold, misroute, and refused delivery, occur on 8-15% of all shipments. Current manual investigation processes require coordinators to query multiple disconnected systems, consuming 60-70% of their time on evidence gathering rather than decision-making. F.A.I.R. addresses this by automating the entire investigation pipeline while maintaining deterministic safety for all financial computations."));
    body.Append(CreateParagraph("The system was evaluated against a 25-case synthetic dataset with 36 automated pytest cases covering boundary conditions, workflow paths, critic rejection, bounded revision loops, and human gate triggers. All tests pass successfully, validating the correctness of deterministic safeguards and agent coordination logic."));

    // Introduction
    body.Append(CreateHeading1("Introduction", "_Toc002"));
    body.Append(CreateHeading2("Business Problem"));
    body.Append(CreateParagraph("Global freight operations handle millions of shipments daily across complex multimodal networks. Despite process improvements, exceptions remain a persistent challenge:"));
    body.Append(CreateBullet("Damage: Cargo arrives with visible or concealed damage requiring carrier claims assessment."));
    body.Append(CreateBullet("Delay: Shipments miss committed delivery windows due to weather, operational failures, or missed connections."));
    body.Append(CreateBullet("Customs Hold: Shipments detained at borders due to documentation issues or regulatory inspections."));
    body.Append(CreateBullet("Misroute: Cargo directed to incorrect hubs or destinations due to label or routing errors."));
    body.Append(CreateBullet("Refused Delivery: Consignees reject cargo due to damage, wrong items, or order cancellations."));
    body.Append(CreateParagraph("Each exception family requires a completely different evidence set and resolution logic. A fixed, one-size-fits-all rule cannot handle the combinatorial complexity of exception type, severity, cargo value, customer tier, SLA terms, and carrier performance."));
    body.Append(CreateHeading2("Why Agency?"));
    body.Append(CreateParagraph("Agency is required because the system must decide what to investigate, how deeply, and when to escalate. Static business rules cannot adapt to the dynamic nature of freight exceptions. A multi-agent architecture provides the necessary flexibility while maintaining deterministic safety through typed state machines, budget enforcement, and adversarial validation."));

    // Proposed Solution
    body.Append(CreateHeading1("Proposed Solution", "_Toc003"));
    body.Append(CreateParagraph("F.A.I.R. introduces five collaborative agents operating on a typed InvestigationState that flows sequentially through the workflow. The architecture implements conditional branching based on exception type, evidence sufficiency, confidence thresholds, and Critic verdicts."));
    body.Append(CreateParagraph("Key design principles:"));
    body.Append(CreateBullet("Deterministic Safety: All monetary calculations are pure Python functions with no LLM involvement."));
    body.Append(CreateBullet("Adversarial Validation: An independent Critic agent tests Resolver conclusions against alternative hypotheses."));
    body.Append(CreateBullet("Human-in-the-Loop: High-risk cases route to human operators for approval, override, or rejection."));
    body.Append(CreateBullet("Full Auditability: Every agent action is recorded in an append-only audit log."));
    body.Append(CreateBullet("Budget Enforcement: Tool calls are limited by severity tier to prevent runaway investigations."));

    // System Architecture
    body.Append(CreateHeading1("System Architecture", "_Toc004"));
    body.Append(CreateParagraph("The F.A.I.R. architecture follows a state-machine pattern where a typed InvestigationState transitions through five agent stages. Conditional branching routes cases based on evidence quality, confidence, and safety thresholds."));
    body.Append(CreateHeading2("State Machine Design"));
    body.Append(CreateParagraph("The InvestigationState dataclass encapsulates the entire case context including the FreightCase, EvidencePlan, EvidenceBundle, ProposedResolution, CriticVerdict, and audit log. State transitions are immutable - each agent returns a new state rather than mutating the existing one."));
    body.Append(CreateHeading2("Conditional Branching"));
    body.Append(CreateBullet("Evidence Gap > 30%: Auto-escalation to human review."));
    body.Append(CreateBullet("Critic REVISE: One bounded revision attempt (max 2 iterations)."));
    body.Append(CreateBullet("Critic REJECT: Immediate human escalation."));
    body.Append(CreateBullet("High Value: Amount > $10,000 triggers mandatory human approval."));
    body.Append(CreateBullet("Low Confidence: Confidence < 0.7 triggers human review."));
    body.Append(CreateBullet("Strategic Customer: All Strategic tier cases require human gate review."));

    // Architecture image
    AddInlineImage(body, mainPart, "/mnt/agents/output/FAIR-Freight-Agentic-Investigation/architecture/architecture.png", "Architecture", ref prId, 14);
    body.Append(CreateCaption("Figure 1: F.A.I.R. System Architecture Diagram"));

    // Agent Design
    body.Append(CreateHeading1("Agent Design", "_Toc005"));
    body.Append(CreateHeading2("Agent 1: Intake & Triage"));
    body.Append(CreateParagraph("Normalizes raw exception events into structured FreightCase objects. Assigns severity based on cargo value thresholds (LOW < $5K, MEDIUM $5K-$15K, HIGH $15K-$50K, CRITICAL > $50K). Sets investigation budget based on severity tier (5-12 tool calls). Determines customer tier implications for downstream liability calculations."));
    body.Append(CreateHeading2("Agent 2: Investigation Planner"));
    body.Append(CreateParagraph("Generates tailored evidence plans per exception family. For DAMAGE cases, the plan includes POD details, damage photos, tracking timeline, carrier performance, and claims history. For DELAY cases, the plan includes weather alerts, SLA terms, and route history. Each plan is dynamically constructed based on exception type."));
    body.Append(CreateHeading2("Agent 3: Evidence Collector"));
    body.Append(CreateParagraph("Executes read-only tool calls against the synthetic SQLite database. Enforces the investigation budget - if the budget is exhausted, remaining tools are skipped and recorded as gaps. Tracks evidence gap ratio (missing / expected) for downstream escalation decisions."));
    body.Append(CreateHeading2("Agent 4: Resolver"));
    body.Append(CreateParagraph("Correlates evidence signals to classify root cause and propose resolution. Uses deterministic rule-based classification with no LLM involvement. Computes resolution amounts using pure functions based on action type, cargo value, and severity. Applies liability caps from customer tier multipliers."));
    body.Append(CreateHeading2("Agent 5: Critic"));
    body.Append(CreateParagraph("Independently validates Resolver conclusions through adversarial checks: tests evidence sufficiency, checks for contradictory facts, evaluates alternative hypotheses, and validates confidence justification. Returns one of three verdicts: VALID, REVISE, or REJECT."));

    // Implementation
    body.Append(CreateHeading1("Implementation", "_Toc006"));
    body.Append(CreateHeading2("Technology Stack"));
    body.Append(CreateDataTable(new string[,] {
        { "Layer", "Technology" },
        { "Language", "Python 3.10+" },
        { "Data Layer", "SQLite with synthetic data" },
        { "UI / PoC", "Streamlit" },
        { "Visualization", "Plotly" },
        { "Testing", "pytest" },
    }));
    body.Append(CreateHeading2("Database Schema"));
    body.Append(CreateParagraph("The synthetic database contains 11 tables with realistic freight data: 60 shipments, 8 carriers, 8 customers, 25 injected exceptions, 200+ tracking events, POD records, damage photos, customs entries, weather alerts, claims history, and SLA terms."));
    body.Append(CreateHeading2("Ten Query Tools"));
    body.Append(CreateParagraph("All tools are read-only SQL SELECT wrappers: get_shipment_info, get_tracking_timeline, get_pod_details, get_damage_photos, get_customs_entry, get_weather_alerts, get_carrier_performance, get_customer_history, get_sla_terms, get_claims_history."));
    body.Append(CreateHeading2("Streamlit UI"));
    body.Append(CreateParagraph("The five-page Streamlit application provides: Exception Queue for browsing cases, Investigation Console for real-time agent trace, Resolution & Approval for human gates, Operations Dashboard for metrics, and Audit & Compliance for full traceability."));

    // Screenshot
    AddInlineImage(body, mainPart, "/mnt/agents/output/FAIR-Freight-Agentic-Investigation/docs/streamlit_console.png", "Streamlit", ref prId, 14);
    body.Append(CreateCaption("Figure 2: Streamlit Investigation Console Screenshot"));

    // Evaluation
    body.Append(CreateHeading1("Evaluation & Testing", "_Toc007"));
    body.Append(CreateParagraph("The system was validated through 36 automated pytest cases organized into six categories:"));
    body.Append(CreateDataTable(new string[,] {
        { "Category", "Tests", "Focus" },
        { "Severity & Budget", "4", "Boundary thresholds for LOW/MEDIUM/HIGH/CRITICAL" },
        { "Evidence Gap", "3", "Zero, threshold, and no-expected scenarios" },
        { "Human Review", "5", "Amount, confidence, critic, tier triggers" },
        { "Resolution", "2", "No-action, credit, and claim calculations" },
        { "Full Workflow", "12", "Damage, delay, customs, misroute, refused paths" },
        { "Critic & Gate", "10", "Rejection, bounded revision, approve/reject" },
    }));
    body.Append(CreateParagraph("All 36 tests pass with 100% success rate, validating the correctness of deterministic safeguards, agent coordination logic, and human gate persistence."));

    // Limitations
    body.Append(CreateHeading1("Limitations & Future Scope", "_Toc008"));
    body.Append(CreateHeading2("Current Limitations"));
    body.Append(CreateBullet("Synthetic data only - no live TMS, carrier, or customs API integrations."));
    body.Append(CreateBullet("Rule-based classification - deterministic logic with no LLM reasoning (Ollama integration possible)."));
    body.Append(CreateBullet("Single-modal evidence - structured data and text only, no image analysis."));
    body.Append(CreateBullet("No real-time streaming - simulated agent trace, not event-driven."));
    body.Append(CreateHeading2("Future Enhancements"));
    body.Append(CreateBullet("Real carrier APIs: integrate live TMS, EDI, and carrier portals."));
    body.Append(CreateBullet("Computer vision: damage assessment from photos using CV models."));
    body.Append(CreateBullet("Predictive prevention: anomaly detection to catch exceptions before they occur."));
    body.Append(CreateBullet("ERP connectors: SAP, Oracle WMS integration for automated resolution execution."));

    // Conclusion
    body.Append(CreateHeading1("Conclusion", "_Toc009"));
    body.Append(CreateParagraph("F.A.I.R. demonstrates that agentic AI can automate freight exception investigation while maintaining deterministic safety and full auditability. The five-agent architecture with adversarial validation and human-in-the-loop governance provides a production-ready blueprint for logistics AI transformation."));
    body.Append(CreateParagraph("Key contributions include: a typed state-machine architecture for multi-agent coordination, deterministic financial safeguards for all monetary computations, an adversarial Critic agent for validation, and comprehensive testing with 36 automated test cases achieving 100% pass rate."));

    // Final section properties
    body.Append(new SectionProperties(
        new HeaderReference { Type = HeaderFooterValues.Default, Id = headerId },
        new FooterReference { Type = HeaderFooterValues.Default, Id = footerId },
        new PageSize { Width = 11906, Height = 16838 },
        new PageMargin { Top = 1800, Right = 1440, Bottom = 1440, Left = 1440, Header = 720, Footer = 720 }));
}

// ========================================================================
// Helpers
// ========================================================================
Paragraph CreateHeading1(string text, string bookmark)
{
    return new Paragraph(
        new ParagraphProperties(new ParagraphStyleId { Val = "Heading1" },
            new BookmarkStart { Name = bookmark, Id = bookmark }),
        new Run(new Text(text)),
        new BookmarkEnd { Id = bookmark });
}

Paragraph CreateHeading2(string text)
{
    return new Paragraph(
        new ParagraphProperties(new ParagraphStyleId { Val = "Heading2" }),
        new Run(new Text(text)));
}

Paragraph CreateParagraph(string text)
{
    return new Paragraph(new Run(new Text(text)));
}

Paragraph CreateBullet(string text)
{
    return new Paragraph(
        new ParagraphProperties(
            new NumberingProperties(new NumberingLevelReference { Val = 0 }, new NumberingId { Val = 1 })),
        new Run(new Text(text)));
}

Paragraph CreateCaption(string text)
{
    return new Paragraph(
        new ParagraphProperties(new ParagraphStyleId { Val = "Caption" }),
        new Run(new Text(text)));
}

Table CreateDataTable(string[,] data)
{
    int cols = data.GetLength(1);
    int rows = data.GetLength(0);
    var tbl = new Table(new TableProperties(
        new TableWidth { Width = "5000", Type = TableWidthUnitValues.Pct },
        new TableBorders(
            new TopBorder { Val = BorderValues.Single, Size = 12, Color = "1a2744" },
            new BottomBorder { Val = BorderValues.Single, Size = 12, Color = "1a2744" },
            new InsideHorizontalBorder { Val = BorderValues.Single, Size = 4, Color = "d8e0dc" })),
        new TableGrid());

    for (int c = 0; c < cols; c++)
        tbl.TableGrid!.Append(new GridColumn());

    for (int r = 0; r < rows; r++)
    {
        var row = new TableRow();
        if (r == 0) row.Append(new TableRowProperties(new TableHeader()));
        for (int c = 0; c < cols; c++)
        {
            var tcp = new TableCellProperties(new TableCellWidth { Width = "0", Type = TableWidthUnitValues.Auto });
            if (r == 0) tcp.Append(new Shading { Val = ShadingPatternValues.Clear, Fill = "f0f4f2" });
            var rpr = new RunProperties(new FontSize { Val = "20" }, new Color { Val = r == 0 ? "1f2937" : "5a6b62" });
            if (r == 0) rpr.Append(new Bold());
            row.Append(new TableCell(tcp, new Paragraph(
                new ParagraphProperties(new Justification { Val = JustificationValues.Center },
                    new SpacingBetweenLines { Before = "40", After = "40" }),
                new Run(rpr, new Text(data[r, c])))));
        }
        tbl.Append(row);
    }
    return tbl;
}

// ========================================================================
// Image helpers
// ========================================================================
string AddImage(MainDocumentPart mp, string path)
{
    var ip = mp.AddImagePart(ImagePartType.Png);
    using var fs = new FileStream(path, FileMode.Open);
    ip.FeedData(fs); return mp.GetIdOfPart(ip);
}

Drawing CreateFloatingBackground(string imgId, uint prId, string name)
{
    return new Drawing(new DW.Anchor(
        new DW.SimplePosition { X = 0, Y = 0 },
        new DW.HorizontalPosition(new DW.PositionOffset("0")) { RelativeFrom = DW.HorizontalRelativePositionValues.Page },
        new DW.VerticalPosition(new DW.PositionOffset("0")) { RelativeFrom = DW.VerticalRelativePositionValues.Page },
        new DW.Extent { Cx = 7560000, Cy = 10692000 },
        new DW.EffectExtent { LeftEdge = 0, TopEdge = 0, RightEdge = 0, BottomEdge = 0 },
        new DW.WrapNone(),
        new DW.DocProperties { Id = prId, Name = name },
        new DW.NonVisualGraphicFrameDrawingProperties(new A.GraphicFrameLocks { NoChangeAspect = true }),
        new A.Graphic(new A.GraphicData(
            new PIC.Picture(
                new PIC.NonVisualPictureProperties(
                    new PIC.NonVisualDrawingProperties { Id = 0, Name = $"{name}.png" },
                    new PIC.NonVisualPictureDrawingProperties()),
                new PIC.BlipFill(new A.Blip { Embed = imgId }, new A.Stretch(new A.FillRectangle())),
                new PIC.ShapeProperties(
                    new A.Transform2D(new A.Offset { X = 0, Y = 0 }, new A.Extents { Cx = 7560000, Cy = 10692000 }),
                    new A.PresetGeometry { Preset = A.ShapeTypeValues.Rectangle })))
        { Uri = "http://schemas.openxmlformats.org/drawingml/2006/picture" }))
    { DistanceFromTop = 0, DistanceFromBottom = 0, DistanceFromLeft = 0, DistanceFromRight = 0,
      SimplePos = false, RelativeHeight = 251658240, BehindDoc = true,
      Locked = false, LayoutInCell = true, AllowOverlap = true });
}

void AddInlineImage(Body body, MainDocumentPart mainPart, string imagePath, string altText, ref uint docPrId, int maxWidthCm = 15)
{
    if (!File.Exists(imagePath)) { Console.Error.WriteLine($"WARNING: Image not found: {imagePath}"); return; }
    var imagePart = mainPart.AddImagePart(ImagePartType.Png);
    byte[] imageBytes = File.ReadAllBytes(imagePath);
    using (var ms = new MemoryStream(imageBytes)) imagePart.FeedData(ms);
    var imageId = mainPart.GetIdOfPart(imagePart);

    int imgWidth, imgHeight;
    using (var ms = new MemoryStream(imageBytes))
    {
        ms.Seek(16, SeekOrigin.Begin);
        byte[] wb = new byte[4], hb = new byte[4];
        ms.Read(wb, 0, 4); ms.Read(hb, 0, 4);
        if (BitConverter.IsLittleEndian) { Array.Reverse(wb); Array.Reverse(hb); }
        imgWidth = BitConverter.ToInt32(wb, 0);
        imgHeight = BitConverter.ToInt32(hb, 0);
    }

    long maxWidthEmu = maxWidthCm * 360000L;
    long cx = maxWidthEmu;
    long cy = (long)(cx * ((double)imgHeight / imgWidth));
    var id = docPrId++;

    body.Append(new Paragraph(
        new ParagraphProperties(new KeepNext(), new Justification { Val = JustificationValues.Center },
            new SpacingBetweenLines { Before = "200", After = "80" }),
        new Run(new Drawing(new DW.Inline(
            new DW.Extent { Cx = cx, Cy = cy },
            new DW.EffectExtent { LeftEdge = 0, TopEdge = 0, RightEdge = 0, BottomEdge = 0 },
            new DW.DocProperties { Id = id, Name = altText },
            new DW.NonVisualGraphicFrameDrawingProperties(new A.GraphicFrameLocks { NoChangeAspect = true }),
            new A.Graphic(new A.GraphicData(
                new PIC.Picture(
                    new PIC.NonVisualPictureProperties(
                        new PIC.NonVisualDrawingProperties { Id = 0, Name = $"{altText}.png" },
                        new PIC.NonVisualPictureDrawingProperties()),
                    new PIC.BlipFill(new A.Blip { Embed = imageId }, new A.Stretch(new A.FillRectangle())),
                    new PIC.ShapeProperties(
                        new A.Transform2D(new A.Offset { X = 0, Y = 0 }, new A.Extents { Cx = cx, Cy = cy }),
                        new A.PresetGeometry { Preset = A.ShapeTypeValues.Rectangle })))
            { Uri = "http://schemas.openxmlformats.org/drawingml/2006/picture" }))
        { DistanceFromTop = 0, DistanceFromBottom = 0, DistanceFromLeft = 0, DistanceFromRight = 0 }))));
}

// ========================================================================
// Settings & Numbering
// ========================================================================
void SetUpdateFieldsOnOpen(MainDocumentPart mp)
{
    var sp = mp.DocumentSettingsPart ?? mp.AddNewPart<DocumentSettingsPart>();
    sp.Settings = new Settings(new UpdateFieldsOnOpen { Val = true }, new DisplayBackgroundShape());
}

void AddNumbering(MainDocumentPart mp)
{
    var np = mp.AddNewPart<NumberingDefinitionsPart>();
    np.Numbering = new Numbering(
        new AbstractNum(new Level(
            new NumberingFormat { Val = NumberFormatValues.Bullet },
            new LevelText { Val = "\u2022" },
            new LevelJustification { Val = LevelJustificationValues.Left },
            new ParagraphProperties(new Indentation { Left = "720", Hanging = "360" })
        ) { LevelIndex = 0 }) { AbstractNumberId = 1 },
        new NumberingInstance(new AbstractNumId { Val = 1 }) { NumberID = 1 });
}
